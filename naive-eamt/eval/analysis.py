#!/usr/bin/env python3
'''
Input file format:

gold files - text with one question per line

evaluation files - jsonl with `translated_text` field

Generates the following files for every gold file found:

input_gold_file.METRIC - scores for all pipelines per question.

input_gold_file.METRIC.best - the best pipeline for each question. If several pipelines were equally the best, this file would have several entries per question.

Post-processing the results:
awk -v FS='\t' '{print $2}' some_gold_file.txt.METRIC.best |sort |uniq -c |sort -rn

With a threshold for scores:
awk -v FS='\t' '$3 >= THRESHOLD {print $2}' some_gold_file.txt.METRIC.best |sort |uniq -c |sort -rn
'''
import argparse
import json
import multiprocessing
import os
import torch
import torchmetrics

def bleu(got, expected, **kwargs):
    'Returns BLEU score, passing all keyword arguments to torchmetrics.functional.bleu_score'
    return torchmetrics.functional.bleu_score([got], [[expected]], **kwargs)

def bleu2(got, expected):
    'Returns BLEU score with n_gram=2'
    return bleu(got, expected, n_gram=2)

def bleu3(got, expected):
    'Returns BLEU score with n_gram=3'
    return bleu(got, expected, n_gram=3)

def bleu4(got, expected):
    'Returns BLEU score with n_gram=4 (default in torchmetrics)'
    return bleu(got, expected, n_gram=4)

def process_task(task, headers, pipelines, metric, output):
    t = open(task)
    ps = map(open, pipelines)
    with open(output, 'w') as o, open(output + '.best', 'w') as o_best:
        o.write('\t'.join(headers) + '\n')
        for inputs in zip(t, *ps):
            expected = inputs[0].rstrip()
            scores = list(map(torch.Tensor.item, (metric(json.loads(inp).get('translated_text', ''), expected) for inp in inputs[1:])))
            o.write('\t'.join(map(str, scores)) + '\n')
            max_score = max(scores)
            for header in (headers[index] for index, score in enumerate(scores) if score == max_score):
                o_best.write('\t'.join((expected, header, str(max_score))) + '\n')

def main(*, path, gold_file_suffix, metric):
    files = sorted(os.listdir(path))
    tasks = [f[:-17] for f in files if f.endswith(gold_file_suffix)]
    with multiprocessing.Pool() as pool:
        for task in tasks:
            filtered_files = [f for f in files if f.startswith(task) and f.endswith('.jsonl') and not f.endswith(gold_file_suffix)]
            headers = [f[len(task) + 1:-6] for f in filtered_files]
            pipelines = [os.path.join(path, f) for f in filtered_files]
            task = os.path.join(path, task + '-en' + gold_file_suffix)
            output = task + '.' + metric.__name__
            #pool.apply_async(process_task, (task, headers, pipelines, metric, output))
            process_task(task, headers, pipelines, metric, output)
    pool.join()

if __name__ == '__main__':
    metrics = [bleu2, bleu3, bleu4]
    metrics_by_name = {f.__name__: f for f in metrics}
    class MetricAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, metrics_by_name[values])
    parser = argparse.ArgumentParser(description='Analyze evaluation files generated with NEAMT')
    parser.add_argument('--path', default='translation_output_all', help='directory with gold and jsonl files')
    parser.add_argument('--gold-file-suffix', default='_gold_file.txt', help='suffix for distinguishing gold files')
    parser.add_argument('--metric', choices=metrics_by_name.keys(), default='bleu4', action=MetricAction, help='which metric to use')
    args = parser.parse_args()
    main(**vars(args))
