# Imports
import json
import time
import requests
from tqdm import tqdm
from statistics import mean

# Load config file
eval_cfg = []
with open('eval_config.json', 'r') as ec:
    eval_cfg = json.load(ec)
print(eval_cfg)

# vars
# error count
count = {
    'error': 0,
    'request': 0,
    'exception': 0
}
url = {
    'execute': "https://beng.dice-research.org/gerbil/execute?",
    'upload': 'https://beng.dice-research.org/gerbil/file/upload',
    'experiment': 'https://beng.dice-research.org/gerbil/experiment?id='
}

bertscore_url = "http://localhost:6150/bertsimilarity"
pred_dir = 'pred_results/'
# output file
output_file = 'experiment_details.tsv'

# Find total number of combinations
for cfg in eval_cfg:
    for lang in cfg['test_cfg']:
        ner_len = len(cfg['test_cfg'][lang]['ner'])
        el_len = len(cfg['test_cfg'][lang]['el'])
        mt_len = len(cfg['test_cfg'][lang]['mt'])
        count['request'] += (ner_len * el_len * mt_len) + mt_len
print('Total number of experiments to be run: %s' % count['request'])


# function to create unique prediction file name
def get_pred_file_name(lang, components):
    return lang + '-' + '-'.join(components)


# Upload file
def upload_file(name, file_path):
    gen_file_name = ''
    # Form the request
    payload = {
        'multiselect': 'NLG',
        'name': name,
        'qlang': ''
    }
    files = [
        ('files', (name + '.txt', open(file_path, 'rb'), 'text/plain'))
    ]
    headers = {}
    # Send the request
    response = requests.request("POST", url['upload'], headers=headers, data=payload, files=files)
    resp_json = response.json()
    # return generated file name
    # print(response.json())
    gen_file_name = resp_json['files'][0]['name']
    return gen_file_name


# Execute experiment
def execute_experiment(pred_file, gold_file):
    # Form the experiment data dict
    payload = "experimentData={\"type\":\"NLG\",\"dataset\":[\"NIFDS_gold(" + gold_file + ")\"],\"hypothesis\":[\"HF_pred(" + pred_file + ")\"],\"candidate\":[],\"language\":\"en\"}"
    # print(payload)
    response = requests.get(url['execute'] + payload)
    # print(response.text)
    return response.text

# Bert Similarity
def get_bertsimilarity(pred_lines, gold_lines):
    payload = json.dumps({
      "predictions": pred_lines,
      "references": gold_lines
    })
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", bertscore_url, headers=headers, data=payload, timeout=600)
    # fetch the f1 scores and average them
    bertscore_f1_arr = response.json()['bert-score']['f1']
    bleurt_arr = response.json()['bleurt']['scores']
    return mean(bertscore_f1_arr), mean(bleurt_arr)


with open(output_file, 'w') as out, tqdm(total=count['request']) as pbar:
    for cfg in eval_cfg:
        test_name = cfg['name']
        pipes = []
        # iterate over languages in the current config
        for lang in cfg['test_cfg']:
            gold_file = test_name + '_%s-en_gold_file' % lang
            # read gold file lines for bert similarity
            with open(gold_file + '.txt',  'r') as gfile:
                gold_file_lines = gfile.read().splitlines()
            # Upload the gold file
            up_gold_file = upload_file(gold_file, gold_file + '.txt')
            ner_comps = cfg['test_cfg'][lang]['ner']
            el_comps = cfg['test_cfg'][lang]['el']
            mt_comps = cfg['test_cfg'][lang]['mt']
            # for each NER
            for ner_item in ner_comps:
                # for each EL
                for el_item in el_comps:
                    # for each MT
                    for mt_item in mt_comps:
                        pipe = [ner_item, el_item, mt_item]
                        # generate pred file name
                        pred_file = pred_dir + test_name + '_' + get_pred_file_name(lang, pipe)
                        # upload pred file
                        up_pred_file = upload_file(pred_file, pred_file + '.txt')
                        # submit experiment
                        exp_id = execute_experiment(up_pred_file, up_gold_file)
                        # bert similarity
                        # read pred file lines for bert similarity
                        with open(pred_file + '.txt',  'r') as pfile:
                            pred_file_lines = pfile.read().splitlines() 
                        bert_f1, bleurt_score = get_bertsimilarity(pred_file_lines, gold_file_lines)
                        # write csv entry
                        out.write('\t'.join(
                            [test_name, lang, str(pipe), gold_file, pred_file, up_gold_file, up_pred_file,
                             url['experiment'] + exp_id, str(bert_f1), str(bleurt_score)]) + '\n')
                        out.flush()
                        # update progress
                        pbar.update(1)
                        # Wait for a few seconds
                        time.sleep(10)
            # append no_ner, no_el MT pipes
            for mt_item in mt_comps:
                pipe = ['no_ner', 'no_el', mt_item]
                # generate pred file name
                pred_file = pred_dir + test_name + '_' + get_pred_file_name(lang, pipe)
                # upload pred file
                up_pred_file = upload_file(pred_file, pred_file + '.txt')
                # submit experiment
                exp_id = execute_experiment(up_pred_file, up_gold_file)
                # bert similarity
                # read pred file lines for bert similarity
                with open(pred_file + '.txt',  'r') as pfile:
                    pred_file_lines = pfile.read().splitlines() 
                bert_f1, bleurt_score = get_bertsimilarity(pred_file_lines, gold_file_lines)
                # write csv entry
                out.write('\t'.join([test_name, lang, str(pipe), gold_file, pred_file, up_gold_file, up_pred_file,
                                     url['experiment'] + exp_id, str(bert_f1), str(bleurt_score)]) + '\n')
                out.flush()
                # update progress
                pbar.update(1)
                # Wait for a few seconds
                # time.sleep(2)

print('Done!')
