#!/usr/bin/env python3
'''
Compute the problematicity of questions.

Examples:
./problematicity.py --lang en --lang de --lang pt --lang es --lang it --lang fr --dataset-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json
'''
from analysis import wd_labels, wd_resolve

import argparse
import logging
import redis
import redis_cache
import tqdm
import analysis
from analysis import mintaka, qald_qae

def mintaka_entities(q):
    return [wd_resolve(entity['name']) for entity in q['questionEntity'] if entity['entityType'] == 'entity' and entity['name'] is not None]

def process_task(input_file, input_format, lang):
    assert isinstance(lang, list)
    len_langs = len(lang)
    output_file = input_file + '.distinctlabels'
    input_data = input_format([input_file])
    with open(output_file, 'w') as output_f:
        for q_id, q in tqdm.tqdm(input_data.items(), desc=input_file):
            try:
                val = max(len(set(wd_labels(uri, lang))) for uri in (m['canonical_uri'] for m in q['ent_mentions'])) / len_langs
            except ValueError:
                val = -1
            output_f.write('\t'.join(map(str, (q_id, val))) + '\n')

def main(*, lang, dataset_file, dataset_format, redis_address):
    global wd_labels
    if redis_address is not None:
        cache = redis_cache.RedisCache(redis_client=redis.StrictRedis(host=redis_address, decode_responses=True))
        wd_labels = cache.cache(namespace='neamt-eval-analysis')(wd_labels)
        analysis.wd_labels = cache.cache(namespace='neamt-eval-analysis')(analysis.wd_labels)
        analysis.dbp_to_wd = cache.cache(namespace='neamt-eval-analysis')(analysis.dbp_to_wd)

    for task in tqdm.tqdm(dataset_file):
        process_task(task, dataset_format, lang)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    formats = {f.__name__: f for f in [mintaka, qald_qae]}
    class FormatAction(argparse.Action):
        def __call__(s, p, n, v, o=None): setattr(n, s.dest, formats[v])

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--lang', required=True, action='append', help='which languages to use for labels')
    parser.add_argument('--dataset-file', nargs='*', default=[], help='original dataset file(s)')
    parser.add_argument('--dataset-format', choices=formats.keys(), default=mintaka, action=FormatAction, help='original dataset format')
    parser.add_argument('--redis-address', help='Redis address for caching')
    args = parser.parse_args()
    main(**vars(args))
