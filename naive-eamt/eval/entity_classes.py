#!/usr/bin/env python3
'''
Retrieve the classes of entities of questions

Examples:
./entity_classes.py --dataset-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json
'''
from analysis import wd_resolve
from wikidata_client import wd_classes

import argparse
import collections
import json
import logging
import redis
import redis_cache
import tqdm

def mintaka_entities(q):
    return [wd_resolve(entity['name']) for entity in q['questionEntity'] if entity['entityType'] == 'entity' and entity['name'] is not None]

def process_task(input_file):
    with open(input_file) as input_f:
        input_data = json.load(input_f)
    classes_questions = collections.Counter()
    classes_labels = {}
    classcount_entities = collections.Counter()
    for q in tqdm.tqdm(input_data, desc=input_file):
        question_classes = []
        for uri in mintaka_entities(q):
            classes = wd_classes(uri)
            classcount_entities[len(classes)] += 1
            question_classes += classes
        if len(question_classes) != 0:
            for cls in question_classes:
                classes_questions[cls['class']] += 1
                classes_labels[cls['class']] = cls['label']
        else:
            classes_questions[''] += 1
            classes_labels[''] = 'no class'
    with open(input_file + '.classes.questions_per_class', 'w') as of:
        of.writelines('\t'.join(map(str, item + (classes_labels[item[0]],))) + '\n' for item in sorted(classes_questions.items(), key=lambda item: item[1], reverse=True))
    with open(input_file + '.classes.classes_per_entity', 'w') as of:
        of.writelines('\t'.join(map(str, (i, classcount_entities[i]))) + '\n' for i in range(max(classcount_entities.keys()) + 1))

def main(*, dataset_file, redis_address):
    global wd_classes
    if redis_address is not None:
        cache = redis_cache.RedisCache(redis_client=redis.StrictRedis(host=redis_address, decode_responses=True))
        wd_classes = cache.cache(namespace='neamt-eval-analysis')(wd_classes)

    for task in tqdm.tqdm(dataset_file, desc='Reading dataset files'):
        process_task(task)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--dataset-file', nargs='*', default=[], help='original dataset file(s)')
    parser.add_argument('--redis-address', help='Redis address for caching')
    args = parser.parse_args()
    main(**vars(args))
