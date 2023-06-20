#!/usr/bin/env python3
'''
Compute per-pipeline average

Example:
./average_analysis.py --path data --problematicity-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.distinctlabels --problematicity-threshold 0.5 --classes-file ~/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.classes
'''
import argparse
import collections
import csv
import logging
import os
import statistics
import tqdm

def read_classes_file(path):
    if path is not None:
        with open(path) as f:
            return {row[0]: row[1:] for row in csv.reader(tqdm.tqdm(f, desc=path), delimiter='\t', quoting=csv.QUOTE_NONE)}
    else:
        return {}

def main(*, path, problematicity_file, classes_file, problematicity_threshold, metric='labels'):
    with open(problematicity_file) as pf:
        question_filter = {q for q, val in (line.split('\t') for line in tqdm.tqdm(pf)) if float(val) >= problematicity_threshold}
    question_classes = read_classes_file(classes_file)
    all_classes = [k for k, v in collections.Counter(c for _, cs in question_classes.items() for c in cs).most_common()]
    files = sorted(os.listdir(path))
    files = [f for f in files if f.endswith('.' + metric)]
    pipelines = set()
    data = collections.defaultdict(dict)
    data_by_class = collections.defaultdict(lambda: collections.defaultdict(list))
    for file in tqdm.tqdm(files, desc='Input files'):
        with open(path + '/' + file, newline='') as f:
            reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
            # first row in header with pipeline names
            headers = next(reader)
            for h in headers[1:]: pipelines.add(h)
            s = [0] * len(headers)
            rows = 0
            for row in tqdm.tqdm(reader):
                # first column is question id
                if row[0] in question_filter:
                    for i, val in list(enumerate(row))[1:]:
                        val = float(val)
                        s[i] += val
                        for question_class in question_classes[row[0]]:
                            data_by_class[headers[i]][question_class].append(val)
                    rows += 1
            for i, val in list(enumerate(s))[1:]: data[headers[i]][file] = val / rows
    pipelines = sorted(pipelines)
    with open(path + '/' + metric + '.thr-' + str(problematicity_threshold) + '.average.languages', 'w', newline='') as of:
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

    if len(question_classes) != 0:
        with open(path + '/' + metric + '.thr-' + str(problematicity_threshold) + '.average.classes', 'w', newline='') as of:
            writer = csv.writer(of, delimiter='\t', quoting=csv.QUOTE_NONE)
            writer.writerow([''] + pipelines)
            for c in all_classes:
                writer.writerow([c] + [statistics.mean(vals) if len(vals) != 0 else None for vals in (data_by_class[p][c] for p in pipelines)])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__.lstrip().split('\n', 2)[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--path', required=True, help='directory with gold and jsonl files')
    parser.add_argument('--problematicity-file', help='question problem metrics')
    parser.add_argument('--problematicity-threshold', type=float, default=0.5, help='only consider questions with problem more than this value')
    parser.add_argument('--classes-file', help='per-question classes list')
    args = parser.parse_args()
    main(**vars(args))
