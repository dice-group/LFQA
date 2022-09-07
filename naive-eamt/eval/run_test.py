import json
import time
import requests
from pathlib import Path
from tqdm import tqdm


url = "http://porque.cs.upb.de:6100/custom-pipeline"
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}
output_dir = 'pred_results/'
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Read Config file
eval_cfg = []
with open('eval_config.json', 'r') as ec:
    eval_cfg= json.load(ec)
print(eval_cfg)

# Function to generate test data using QALD file
def get_qald_test_data(filename):
    qald_json = {}
    res_data = {}
    with open('qald10/qald_10.json','r') as qald_file:
        qald_json = json.load(qald_file)
    # Find all langauges
    for item in qald_json['questions'][0]['question']:
        lang = item['language']
        res_data[lang] = []
    for q_item in qald_json['questions']:
        for q_pair in q_item['question']:
           res_data[q_pair['language']].append(q_pair['string'])
    return res_data

test_pipelines = {}
total_req_count = 0
for cfg in eval_cfg:
    lang_comp_count = 0
    test_name = cfg['name']
    pipes = []
    test_data = []
    if 'QALD' in test_name:
        test_data = get_qald_test_data(cfg['file'])
    for lang in cfg['test_cfg']:
        ner_comps = cfg['test_cfg'][lang]['ner']
        el_comps = cfg['test_cfg'][lang]['el']
        mt_comps = cfg['test_cfg'][lang]['mt']
        lang_comps = []
        # for each NER
        for ner_item in ner_comps:
            # for each EL
            for el_item in el_comps:
                # for each MT
                for mt_item in mt_comps:
                    lang_comps.append([ner_item, el_item, mt_item])
                    lang_comp_count += 1
        pipes.append((lang, lang_comps))
    test_pipelines[test_name] = {}
    test_pipelines[test_name]['pipelines'] = pipes
    test_pipelines[test_name]['data'] = test_data
    total_req_count += lang_comp_count * len(test_data['en'])
    # Write test data to a file
    with open(test_name + '_en_gold_file.txt', 'w') as out:
        # For each test string
        for query in test_data['en']:
            out.write(query + '\n')
print('Total request count:', total_req_count)

print('Test Pipelines:\n',test_pipelines['QALD10-MT']['pipelines'])

# function to create unique prediction file name
def get_pred_file_name(lang, components):
    return lang + '-' + '-'.join(components)

# Create HTTP request object
def get_translation(query, components):
    # print('Getting Translation for: ', query)
    payload={
        'query': query,
        'components': ','.join(components)
    }
    response = requests.request("POST", url, headers=headers, data=payload, timeout=20)
    # print('Translation received: ', response.text)
    if response.status_code != 200:
        print('error encountered for the query %s and components %s. Response: \n %s'%(query, payload['components'], response))
        return ''
    return response.text

# setup progress bar
with tqdm(total=total_req_count) as pbar:
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
                # Create a prediction file
                pred_file = test + '_' + get_pred_file_name(lang, pipeline) + '.txt'
                with open(output_dir + pred_file, 'w') as out:
                    # For each test string
                    for query in test_data[lang]:
                        # Get the prediction
                        # print('Pipeline:', pipeline)
                        out.write(get_translation(query, pipeline) + '\n')
                        pbar.update(1)
                        # To avoid 'too many requests' to SPARQL endpoints
                        time.sleep(0.5)