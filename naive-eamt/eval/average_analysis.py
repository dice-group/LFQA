#!/usr/bin/env python3
'''
Compute per-pipeline average
'''
import argparse
import collections
import csv
import logging
import os
import statistics
import tqdm

def main(*, path, problematicity_file, problematicity_threshold, metric='labels'):
    with open(problematicity_file) as pf:
        question_filter = {q for q, val in (line.split('\t') for line in tqdm.tqdm(pf)) if float(val) >= problematicity_threshold}
    files = sorted(os.listdir(path))
    files = [f for f in files if f.endswith('.' + metric)]
    pipelines = set()
    data = collections.defaultdict(dict)
    for file in files:
        with open(path + '/' + file, newline='') as f:
            reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
            headers = next(reader)
            for h in headers[1:]: pipelines.add(h)
            s = [0] * len(headers)
            rows = 0
            for row in tqdm.tqdm(reader):
                if row[0] in question_filter:
                    for i, val in list(enumerate(row))[1:]: s[i] += float(val)
                    rows += 1
            for i, val in list(enumerate(s))[1:]: data[headers[i]][file] = val / rows
    pipelines = list(pipelines)
    with open(path + '/' + metric + '.thr-' + str(problematicity_threshold) + '.average', 'w', newline='') as of:
        writer = csv.writer(of, delimiter='\t', quoting=csv.QUOTE_NONE)
        writer.writerow([''] + pipelines)
        for file in files:
            writer.writerow([file] + [data[p].get(file) for p in pipelines])

    groups = [
        ('no_ner-no_el-no_ft', lambda p: 'no_ner-no_el-' in p and '_plc_ft_mt' not in p),
        ('ner-el', lambda p: 'no_ner-no_el-' not in p),
    ]
    with open(path + '/' + metric + '.thr-' + str(problematicity_threshold) + '.average.groups', 'w', newline='') as of:
        writer = csv.writer(of, delimiter='\t', quoting=csv.QUOTE_NONE)
        writer.writerow([''] + [name for name, _ in groups])
        for file in files:
            writer.writerow([file] + [statistics.mean(data[p].get(file) for p in pipelines if fun(p) and file in data[p]) for _, fun in groups])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--path', required=True, help='directory with gold and jsonl files')
    parser.add_argument('--problematicity-file', help='question problem metrics')
    parser.add_argument('--problematicity-threshold', type=float, default=0.5, help='only consider questions with problem more than this value')
    args = parser.parse_args()
    main(**vars(args))
