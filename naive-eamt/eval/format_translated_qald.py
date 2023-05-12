# Script to convert translations into QALD format
# For each QALD file
    # Read the QALD file
    # For each QALD question
        # map the english text against the object
    # For each gold file
        # Read all lines to an array
        # For each translation file
            # Read all lines to an array
            # starting with index 0
                # find the QALD object for gold english text
                # create a new object with translated english text
                # save the object in json
# Imports
import json
from pathlib import Path
import copy

# vars
# error count
count = {
    'error': 0,
    'request': 0,
    'exception': 0
}
pred_dir = 'pred_results/'
# output directory
output_dir = 'translated_qald/'

# Create the directory(s) in the output path
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Read Config for QALD file
# Load config file
eval_cfg = []
with open('config/eval_config.json', 'r') as ec:
    eval_cfg = json.load(ec)
print(eval_cfg)


# function to create unique prediction file name
def get_pred_file_name(lang, components):
    return lang + '-' + '-'.join(components)


def write_translated_qald(lang, pipe, pred_dir, test_name, output_dir, gold_translations):
    # Output QALD
    out_qald = {"questions": []}
    # For each translation file
    pred_file = pred_dir + test_name + '_' + get_pred_file_name(lang, pipe) + '.txt'
    # Read all lines to an array
    pred_translations = []
    with open(pred_file, 'r') as pred_fin:
        pred_translations = pred_fin.readlines()
    # starting with index 0
    for i in range(len(gold_translations)):
        # find the QALD object for gold english text
        gold_str = gold_translations[i]
        qald_obj = copy.deepcopy(q_map[gold_str.strip()])
        # extract language specific string to keep for reference
        lang_spec_q = None
        for qstr_pair in qald_obj['question']:
            if qstr_pair['language'] == lang:
                lang_spec_q = qstr_pair
                break
        # create a new object with translated english text
        qald_obj['question'] = [{'language': 'en', 'string': pred_translations[i].strip()}, lang_spec_q]
        # save the object in json
        out_qald["questions"].append(qald_obj)
    # Save the QALD output
    qald_out_file = output_dir + test_name + '_' + get_pred_file_name(lang, pipe) + '.json'
    with open(qald_out_file, 'w') as f:
        json.dump(out_qald, f, indent=4)


for cfg in eval_cfg:
    test_name = cfg['name']
    if 'QALD' not in test_name:
        continue
    # Read the QALD file
    qald_file = cfg['file']
    qald_json = None

    with open(qald_file, 'r') as file:
        qald_json = json.load(file)
    q_map = {}
    # For each QALD question
    for q_item in qald_json['questions']:
        for q_pair in q_item['question']:
            lang = q_pair['language']
            if lang == 'en':
                # map the english text against the object
                q_map[q_pair['string']] = q_item
                break
    # iterate over languages in the current config
    for lang in cfg['test_cfg']:
        # For each gold file
        gold_file = test_name + '_%s-en_gold_file' % lang + '.txt'
        # Read all lines to an array
        gold_translations = []
        with open(gold_file, 'r') as gold_fin:
            gold_translations = gold_fin.readlines()
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
                    # write the translated QALD
                    write_translated_qald(lang, pipe, pred_dir, test_name, output_dir, gold_translations)

        # append no_ner, no_el MT pipes
        for mt_item in mt_comps:
            pipe = ['no_ner', 'no_el', mt_item]
            # write the translated QALD
            write_translated_qald(lang, pipe, pred_dir, test_name, output_dir, gold_translations)

print('Done!')
