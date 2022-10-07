# This script is to help generate the translations for the defined test configuration
import json
import logging
import time
import requests
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool

pool = Pool(processes=28)

# URL to the custom NEAMT pipeline
url = "http://localhost:6100/custom-pipeline"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
# Output directory to store the translation files to
output_dir = 'pred_results/'
# Create the directory(s) in the output path
Path(output_dir).mkdir(parents=True, exist_ok=True)
# error count
count = {
    'error': 0,
    'request': 0,
    'exception': 0
}
# Read Config file
eval_cfg = []
with open('eval_config.json', 'r') as ec:
    eval_cfg = json.load(ec)

print(eval_cfg)


# Function to generate test data using QALD file
def get_qald_test_data(filename):
    qald_json = {}
    res_data = {}
    with open(filename, 'r') as qald_file:
        qald_json = json.load(qald_file)
    for q_item in qald_json['questions']:
        id = q_item['id']
        for q_pair in q_item['question']:
            lang = q_pair['language']
            if lang not in res_data:
                res_data[lang] = {}
            res_data[lang][id] = q_pair['string']
    return res_data


# Go through the configuration to form the translation pipelines
test_pipelines = {}

for cfg in eval_cfg:
    test_name = cfg['name']
    pipes = []
    test_data = []
    if 'QALD' in test_name:
        test_data = get_qald_test_data(cfg['file'])
    # print data statistics
    for lang in test_data:
        print('[%s] %s language entries: %d' % (test_name, lang, len(test_data[lang])))
    # iterate over languages in the current config
    for lang in cfg['test_cfg']:
        ner_comps = cfg['test_cfg'][lang]['ner']
        el_comps = cfg['test_cfg'][lang]['el']
        mt_comps = cfg['test_cfg'][lang]['mt']
        lang_pipes = []
        # for each NER
        for ner_item in ner_comps:
            # for each EL
            for el_item in el_comps:
                # for each MT
                for mt_item in mt_comps:
                    lang_pipes.append([ner_item, el_item, mt_item])
        # append no_ner, no_el MT pipes
        # for mt_item in mt_comps:
        #     lang_pipes.append(['no_ner', 'no_el', mt_item])
        pipes.append((lang, lang_pipes))
        count['request'] += (len(lang_pipes) * len(test_data[lang]))
        # Write test data to a file for each lang -> en combination
        with open(test_name + '_%s-en_gold_file.txt' % lang, 'w') as out:
            # For each test string
            for id in test_data[lang]:
                out.write(test_data['en'][id] + '\n')

    test_pipelines[test_name] = {}
    test_pipelines[test_name]['pipelines'] = pipes
    test_pipelines[test_name]['data'] = test_data

print('Total request count:', count['request'])

for test in test_pipelines:
    print('Test Pipelines for %s:\n' % test, test_pipelines[test]['pipelines'])

# function to create unique prediction file name
def get_pred_file_name(lang, components):
    return lang + '-' + '-'.join(components)


# Function to fetch the transation through a HTTP POST request
def get_translation(query, components):
    # print('Getting Translation for: ', query)
    payload = {
        'query': query,
        'components': ','.join(components)
    }
    ret_val = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=600)
        # print('Translation received: ', response.text)
        if response.status_code != 200:
            print('error encountered for the query %s and components %s. Response: \n %s' % (
                query, payload['components'], response))
            count['error'] += 1
        else:
            ret_val = response.text
    except Exception as e:
        print('Following exception encountered for the query %s: %s' % (query, e))
        count['exception'] += 1

    return ret_val
# function that can be run in parallel
def execute_pipeline(lang, pipeline, output_dir, test, test_data, pbar):
    # Create a prediction file
    pred_file = test + '_' + get_pred_file_name(lang, pipeline) + '.txt'
    with open(output_dir + pred_file, 'w') as out:
        # For each test string
        for id in test_data[lang]:
            # Get the prediction
            # print('Pipeline:', pipeline)
            query = test_data[lang][id]
            out.write(get_translation(query, pipeline) + '\n')
            pbar.update(1)

# setup progress bar
with tqdm(total=count['request']) as pbar:
    # for each config
    for test in test_pipelines:
        test_data = test_pipelines[test]['data']
        lang_pipelines = test_pipelines[test]['pipelines']
        # For each pipeline-lang pair
        for pipeline_pair in lang_pipelines:
            lang = pipeline_pair[0]
            pipelines = pipeline_pair[1]
            # for each pipeline
            for pipeline in pipelines:
                pool.apply_async(execute_pipeline, [lang, pipeline, output_dir, test, test_data, pbar])
# Server errors
print('Total error count: %d' % count['error'])
# Exceptions in the test script
print('Total exception count: %d' % count['exception'])
