#!/usr/bin/env python3
'''
Retrieve the classes of entities of questions

Examples:
./entity_classes.py --dataset-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json
'''
from wikidata_client import wd_classes

import argparse
import collections
import logging
import redis
import redis_cache
import tqdm
import analysis
from analysis import mintaka, qald_qae

def process_task(input_file, input_format):
    input_data = input_format([input_file])
    classes_questions = collections.Counter()
    classes_labels = {}
    classcount_entities = collections.Counter()
    with open(input_file + '.classes', 'w') as question_classes_o:
        for q_id, q in tqdm.tqdm(input_data.items(), desc=input_file):
            question_classes = set()
            for uri in (m['canonical_uri'] for m in q['ent_mentions']):
                classes = wd_classes(uri)
                classcount_entities[len(classes)] += 1
                question_classes |= {c['class'] for c in classes}
                for cls in classes:
                    classes_labels[cls['class']] = cls['label'] if cls['label'] is not None else '(None)'
                question_classes_o.write('\t'.join([q_id] + sorted(question_classes)) + '\n')
            if len(question_classes) != 0:
                for cls in question_classes:
                    classes_questions[cls] += 1
            else:
                classes_questions[''] += 1
                classes_labels[''] = '(no class)'
    of_path = input_file + '.classes.questions_per_class'
    logging.info('Writing file: %s', of_path)
    with open(of_path, 'w') as of:
        of.writelines('\t'.join(map(str, item + (classes_labels[item[0]],))) + '\n' for item in sorted(classes_questions.items(), key=lambda item: item[1], reverse=True))
    of_path = input_file + '.classes.classes_per_entity'
    logging.info('Writing file: %s', of_path)
    with open(of_path, 'w') as of:
        of.writelines('\t'.join(map(str, (i, classcount_entities[i]))) + '\n' for i in range(max(classcount_entities.keys()) + 1))

def main(*, dataset_file, dataset_format, redis_address):
    global wd_classes
    if redis_address is not None:
        cache = redis_cache.RedisCache(redis_client=redis.StrictRedis(host=redis_address, decode_responses=True))
        wd_classes = cache.cache(namespace='neamt-eval-analysis')(wd_classes)
        analysis.wd_labels = cache.cache(namespace='neamt-eval-analysis')(analysis.wd_labels)
        analysis.dbp_to_wd = cache.cache(namespace='neamt-eval-analysis')(analysis.dbp_to_wd)

    for task in tqdm.tqdm(dataset_file, desc='Reading dataset files'):
        process_task(task, dataset_format)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    formats = {f.__name__: f for f in [mintaka, qald_qae]}
    class FormatAction(argparse.Action):
        def __call__(s, p, n, v, o=None): setattr(n, s.dest, formats[v])

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--dataset-file', nargs='*', default=[], help='original dataset file(s)')
    parser.add_argument('--dataset-format', choices=formats.keys(), default=mintaka, action=FormatAction, help='original dataset format')
    parser.add_argument('--redis-address', help='Redis address for caching')
    args = parser.parse_args()
    main(**vars(args))
