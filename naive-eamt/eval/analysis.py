#!/usr/bin/env python3
'''
Input file format:

gold files - text with one question per line

evaluation files - jsonl with `translated_text` field

Generates the following files for every gold file found:

input_gold_file.METRIC - scores for all pipelines per question.

input_gold_file.METRIC.best - the best pipeline for each question. If several pipelines were equally the best, this file would have several entries per question.

Examples:

./analysis.py --redis-address localhost --path translation_output_all/QALD9Plus --metric entitiesfound --dataset-format=qald_qae --dataset-file ~/.local/share/datasets/qald-9-plus-query-entities.json

./analysis.py --redis-address localhost --path translation_output_all/QALD10 --metric entitiesfound --dataset-format=qald_qae --dataset-file ~/.local/share/datasets/qald-10-query-entities.json
'''
import argparse
import collections
import itertools
import json
import logging
import multiprocessing
import os
import re
import redis
import redis_cache
import torch
import torchmetrics
import tqdm
import SPARQLWrapper

WD = 'http://www.wikidata.org/entity/'

def bleu2(got, expected):
    'Returns BLEU score with n_gram=2'
    return torchmetrics.functional.bleu_score([got.get('translated_text', '')], [[expected['text']]], n_gram=2).item()

def bleu3(got, expected):
    'Returns BLEU score with n_gram=3'
    return torchmetrics.functional.bleu_score([got.get('translated_text', '')], [[expected['text']]], n_gram=3).item()

def bleu4(got, expected):
    'Returns BLEU score with n_gram=4 (default in torchmetrics)'
    return torchmetrics.functional.bleu_score([got.get('translated_text', '')], [[expected['text']]], n_gram=4).item()

def jaccard(got, expected):
    'Jaccard similarity coefficient for sets'
    got_set = set(m['canonical_uri'] for m in got.get('ent_mentions', []) if 'canonical_uri' in m)
    expected_set = set(m['canonical_uri'] for m in expected.get('ent_mentions', []) if 'canonical_uri' in m)
    u = len(got_set | expected_set)
    i = len(got_set & expected_set)
    return i / u if u != 0 else 0 if i != 0 else 1

def entitiesfound(got, expected):
    'Ratio of entities which were found, without penalizing additional found entities'
    got_set = set(m['canonical_uri'] for m in got.get('ent_mentions', []) if 'canonical_uri' in m)
    expected_set = set(m['canonical_uri'] for m in expected.get('ent_mentions', []) if 'canonical_uri' in m)
    expected_len = len(expected_set)
    return len(got_set & expected_set) / expected_len if expected_len != 0 else 1

def labels(got, expected):
    'Check if any of entity labels from expected result are found in the translated text we got'
    mentions = [m for m in expected.get('ent_mentions', []) if len(m.get('labels', [])) != 0]
    if (l := len(mentions)) != 0:
        t = got.get('translated_text', '')
        return sum(1 for m in mentions if any(s.lower() in t for s in m['labels'])) / l
    else:
        return 1

def wd_resolve(local_name):
    # may need urllib.parse.urljoin
    return WD + local_name

def dbpedia_endpoint_uri(dbp_uri):
    if dbp_uri.startswith('http://dbpedia.org/'):
        return 'https://dbpedia.org/sparql'
    elif match := re.match('^http://([a-z]{2})\\.dbpedia\\.org/', dbp_uri):
        return 'http://' + match[1] + '.dbpedia.org/sparql'
    else:
        raise Exception('Unknown DBPedia URI: ' + dbp_uri)

dbp_to_wd_sparql = {}
def dbp_to_wd(dbp_uri):
    global dbp_to_wd_sparql
    endpoint_uri = dbpedia_endpoint_uri(dbp_uri)
    if endpoint_uri not in dbp_to_wd_sparql:
        dbp_to_wd_sparql[endpoint_uri] = SPARQLWrapper.SPARQLWrapper(endpoint_uri)
        dbp_to_wd_sparql[endpoint_uri].setReturnFormat(SPARQLWrapper.JSON)
    dbp_to_wd_sparql[endpoint_uri].setQuery('SELECT DISTINCT ?uri WHERE {<' + dbp_uri + '> owl:sameAs ?uri. FILTER(strstarts(str(?uri), "http://www.wikidata.org/entity/"))}')
    bindings = dbp_to_wd_sparql[endpoint_uri].queryAndConvert()['results']['bindings']
    return bindings[0]['uri']['value'] if len(bindings) != 0 else None

def resolve(link):
    'Automatically detect and resolve links, outputs WD entity link or None'
    if link.startswith('http://www.wikidata.org/entity/'):
        return link
    elif link.startswith('http://dbpedia.org/resource/'):
        return dbp_to_wd(link)
    elif link.startswith('http://www.wikidata.org/prop/') \
    or link.startswith('http://dbpedia.org/ontology/') \
    or link.startswith('http://dbpedia.org/property/') \
    or link.startswith('http://dbpedia.org/class/') \
    or link.startswith('http://www.w3.org/1999/02/22-rdf-syntax-ns#') \
    or link.startswith('http://www.w3.org/2000/01/rdf-schema#') \
    or link.startswith('http://www.w3.org/2004/02/skos/core#') \
    or link.startswith('http://purl.org/dc/terms/') \
    or link.startswith('http://xmlns.com/foaf/0.1/') \
    or link.startswith('http://wikiba.se/ontology#'):
        return None
    else:
        raise Exception('Unknown link: ' + link)

def neamt(item):
    'Fixes WD links in NEAMT output items from jsonl, and changes DBP links to WD links'
    if 'ent_mentions' in item and 'kb' in item:
        if item['kb'] == 'wd':
            resolver = wd_resolve
        elif item['kb'] == 'dbp':
            resolver = dbp_to_wd
        else:
            raise Exception('Unknown kb: ' + item['kb'])
        for mention in item['ent_mentions']:
            if 'link' in mention:
                uri = resolver(mention['link'])
                if uri is not None:
                    mention['canonical_uri']= uri
                else:
                    logging.warn('Could not resolve link: %s', mention['link'])
    return item

def qald_qae(dataset_file):
    def qae_mentions(mentions):
        return [{
            'canonical_uri': uri,
        } for uri in (resolve(m['link']) for m in mentions) if uri is not None]
    questions = dict()
    for df in tqdm.tqdm(dataset_file, desc='Reading datasets'):
        with open(df) as f:
            questions |= {str(q['id']): {
                'text': q['question'],
                'ent_mentions': qae_mentions(q['query_ent_mentions'] or []),
            } for q in tqdm.tqdm(json.load(f), desc=df)}
    logging.info('%d questions in the dataset', len(questions))
    return lambda q_id: questions.get(q_id)

def mintaka(dataset_file):
    def mintaka_mentions(mentions):
        return [{
            'canonical_uri': wd_resolve(m['name']),
            'labels': {m['label'], m['mention']},
        } for m in mentions if m['entityType'] == 'entity' and m['name'] is not None]
    questions = dict()
    for df in dataset_file:
        with open(df) as f:
            questions |= {q['id']: {
                'text': q['question'],
                'ent_mentions': mintaka_mentions(q['questionEntity']),
            } for q in tqdm.tqdm(json.load(f))}
    logging.info('%d questions in the dataset', len(questions))
    return lambda q_id: questions.get(q_id)

def process_task(task, headers, pipelines, metric, output, dataset_lu):
    #logging.info('Processing: %s', task)
    best_count = collections.Counter()
    # FIXME t ends with .txt or .tsv
    if task.endswith('.tsv'):
        # Custom format, tab-separated ID and question in a line
        t = map(lambda line: line.split('\t')[:2], map(str.rstrip, tqdm.tqdm(open(task), desc=task)))
    else: # ends with '.txt'?
        # Custom format, one question per line
        # ID is not provided
        t = itertools.zip_longest((), map(str.rstrip, open(task)))
    ps = map(open, pipelines)
    with open(output, 'w') as o, open(output + '.best', 'w') as o_best:
        o.write('\t'.join(headers) + '\n')
        for inputs in zip(t, *ps):
            q_id, q_text = inputs[0]
            if dataset_lu is not None and q_id is not None:
                expected = dataset_lu(q_id)
                assert expected is not None
            else:
                expected = {'text': q_text}
            scores = list(metric(neamt(json.loads(inp)), expected) for inp in inputs[1:])
            o.write('\t'.join(map(str, scores)) + '\n')
            max_score = max(scores)
            for header in (headers[index] for index, score in enumerate(scores) if score == max_score):
                o_best.write('\t'.join((q_id, expected['text'], header, str(max_score))) + '\n')
                best_count[header] += 1
    with open(output + '.best.count', 'w') as o_best_count:
        o_best_count.writelines('\t'.join(map(str, item)) + '\n' for item in sorted(best_count.items(), key=lambda item: item[1], reverse=True))

def main(*, path, gold_file_suffix, metric, dataset_file, dataset_format, redis_address):
    global dbp_to_wd
    if redis_address is not None:
        cache = redis_cache.RedisCache(redis_client=redis.StrictRedis(host=redis_address, decode_responses=True))
        dbp_to_wd = cache.cache(namespace='neamt-eval-analysis')(dbp_to_wd)
    files = sorted(os.listdir(path))
    tasks = [f[:-17] for f in files if f.endswith(gold_file_suffix)]
    dataset_lu = dataset_format(dataset_file) if dataset_file is not None else None
    with multiprocessing.Pool() as pool:
        for task in tqdm.tqdm(tasks):
            filtered_files = [f for f in files if f.startswith(task) and f.endswith('.jsonl') and not f.endswith(gold_file_suffix)]
            headers = [f[len(task) + 1:-6] for f in filtered_files]
            pipelines = [os.path.join(path, f) for f in filtered_files]
            task = os.path.join(path, task + '-en' + gold_file_suffix)
            output = task + '.' + metric.__name__
            #pool.apply_async(process_task, (task, headers, pipelines, metric, output, dataset_lu))
            process_task(task, headers, pipelines, metric, output, dataset_lu)
    pool.close()
    pool.join()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    metrics = {f.__name__: f for f in [bleu2, bleu3, bleu4, jaccard, entitiesfound, labels]}
    class MetricAction(argparse.Action):
        def __call__(s, p, n, v, o=None): setattr(n, s.dest, metrics[v])

    formats = {f.__name__: f for f in [mintaka, qald_qae]}
    class FormatAction(argparse.Action):
        def __call__(s, p, n, v, o=None): setattr(n, s.dest, formats[v])

    parser = argparse.ArgumentParser(description='Analyze evaluation files generated with NEAMT')
    parser.add_argument('--path', default='translation_output_all', help='directory with gold and jsonl files')
    parser.add_argument('--gold-file-suffix', default='_gold_file.tsv', help='suffix for distinguishing gold files')
    parser.add_argument('--metric', choices=metrics.keys(), default=bleu4, action=MetricAction, help='which metric to use')
    parser.add_argument('--dataset-file', nargs='*', default=[], help='original dataset file(s)')
    parser.add_argument('--dataset-format', choices=formats.keys(), default=mintaka, action=FormatAction, help='original dataset format')
    parser.add_argument('--redis-address', help='Redis address for caching')
    args = parser.parse_args()
    main(**vars(args))
