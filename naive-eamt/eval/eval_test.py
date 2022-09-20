# Imports
import json
import time
import requests
from tqdm import tqdm

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


with open(output_file, 'w') as out, tqdm(total=count['request']) as pbar:
    for cfg in eval_cfg:
        test_name = cfg['name']
        pipes = []
        # iterate over languages in the current config
        for lang in cfg['test_cfg']:
            gold_file = test_name + '_%s-en_gold_file' % lang
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
                        # write csv entry
                        out.write('\t'.join(
                            [test_name, lang, str(pipe), gold_file, pred_file, up_gold_file, up_pred_file,
                             url['experiment'] + exp_id]) + '\n')
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
                # write csv entry
                out.write('\t'.join([test_name, lang, str(pipe), gold_file, pred_file, up_gold_file, up_pred_file,
                                     url['experiment'] + exp_id]) + '\n')
                out.flush()
                # update progress
                pbar.update(1)
                # Wait for a few seconds
                time.sleep(10)

print('Done!')
