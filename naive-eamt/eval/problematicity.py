#!/usr/bin/env python3
'''
Compute the problematicity of questions.

Examples:
./problematicity.py --lang en --lang de --lang pt --lang es --lang it --lang fr --dataset-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json
'''
from analysis import wd_labels, wd_resolve

import argparse
import json
import logging
import redis
import redis_cache
import tqdm

def mintaka_entities(q):
    return [wd_resolve(entity['name']) for entity in q['questionEntity'] if entity['entityType'] == 'entity' and entity['name'] is not None]

def process_task(input_file, lang):
    assert isinstance(lang, list)
    len_langs = len(lang)
    output_file = input_file + '.distinctlabels'
    with open(input_file) as input_f:
        input_data = json.load(input_f)
    with open(output_file, 'w') as output_f:
        for q in tqdm.tqdm(input_data, desc=input_file):
            try:
                val = max(len(set(wd_labels(uri, lang))) for uri in mintaka_entities(q)) / len_langs
            except ValueError:
                val = -1
            output_f.write('\t'.join(map(str, (q['id'], val))) + '\n')

def main(*, lang, dataset_file, redis_address):
    global wd_labels
    if redis_address is not None:
        cache = redis_cache.RedisCache(redis_client=redis.StrictRedis(host=redis_address, decode_responses=True))
        wd_labels = cache.cache(namespace='neamt-eval-analysis')(wd_labels)

    for task in tqdm.tqdm(dataset_file):
        process_task(task, lang)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--lang', required=True, action='append', help='which languages to use for labels')
    parser.add_argument('--dataset-file', nargs='*', default=[], help='original dataset file(s)')
    parser.add_argument('--redis-address', help='Redis address for caching')
    args = parser.parse_args()
    main(**vars(args))
