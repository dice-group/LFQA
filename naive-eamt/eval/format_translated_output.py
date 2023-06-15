# Imports
import json
from pathlib import Path
import copy
import logging
import sys
'''
This script formats the translations obtained from "run_test.py" into original input format, e.g: QALD, MINTAKA.
Example usage:
python format_translated_output.py  "translation_output/" "translated_qald/" "config/eval_config.json"
'''
# Set logging format
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
args = sys.argv[1:]

# vars
# error count
count = {
    'error': 0,
    'request': 0,
    'exception': 0
}
# directory with files generated using neamt
pred_dir = 'translation_output/'
# output directory
output_dir = 'translated_qald/'
# evaluation config file
eval_config_file = 'config/eval_config.json'

if len(args) == 3:
    pred_dir = args[0]
    output_dir = args[1]
    eval_config_file = args[2]

# Create the directory(s) in the output path
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Read Config for QALD file
# Load config file
eval_cfg = []
with open(eval_config_file, 'r') as ec:
    eval_cfg = json.load(ec)
logging.info(eval_cfg)


# function to create unique prediction file name
def get_pred_file_name(lang, components):
    return lang + '-' + '-'.join(components)


def write_translated_qald(lang, pipe, pred_dir, test_name, output_dir, gold_translations, q_map):
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


def write_translated_mintaka(lang, pipe, pred_dir, test_name, output_dir, gold_translations, q_map):
    # Output QALD
    output_json = []
    # For each translation file
    pred_file = pred_dir + test_name + '_' + get_pred_file_name(lang, pipe) + '.txt'
    # Read all lines to an array
    with open(pred_file, 'r') as pred_fin:
        pred_translations = pred_fin.readlines()
    # starting with index 0
    for i in range(len(gold_translations)):
        # find the QALD object for gold english text
        gold_str = gold_translations[i]
        mintaka_obj = copy.deepcopy(q_map[gold_str.strip()])
        # extract language specific string to keep for reference
        lang_spec_q = None
        mintaka_obj['translations'] = { lang :  mintaka_obj['translations'][lang] }
        # create a new object with translated english text
        mintaka_obj['question'] = pred_translations[i].strip()
        # Empty the existing question entity information as its invalid for the translated query
        mintaka_obj['questionEntity'] = []
        # save the object in json
        output_json.append(mintaka_obj)
    # Save the QALD output
    mintaka_out_file = output_dir + test_name + '_' + get_pred_file_name(lang, pipe) + '.json'
    with open(mintaka_out_file, 'w') as f:
        json.dump(output_json, f, indent=4)

def fetch_qald_question_map(qald_file_path):

    with open(qald_file_path, 'r') as file:
        qald_json = json.load(file)
    res_map = {}
    # For each QALD question
    for q_item in qald_json['questions']:
        for q_pair in q_item['question']:
            lang = q_pair['language']
            if lang == 'en':
                # map the english text against the object
                res_map[q_pair['string']] = q_item
                break
    return res_map

def fetch_mintaka_question_map(mintaka_file_path):

    with open(mintaka_file_path, 'r') as file:
        mintaka_json = json.load(file)
    res_map = {}
    for q_item in mintaka_json:
        res_map[q_item['question']] = q_item
    return res_map


for cfg in eval_cfg:
    test_name = cfg['name']
    if 'QALD' in test_name:
        write_translation = write_translated_qald
        fetch_questions = fetch_qald_question_map
    elif 'MINTAKA' in test_name:
        write_translation = write_translated_mintaka
        fetch_questions = fetch_mintaka_question_map
    else:
        continue

    q_map = fetch_questions(cfg['file'])
    # iterate over languages in the current config
    for lang in cfg['test_cfg']:
        # For each gold file
        gold_file = pred_dir + test_name + '_%s-en_gold_file' % lang + '.txt'
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
                    write_translation(lang, pipe, pred_dir, test_name, output_dir, gold_translations, q_map)

        # append no_ner, no_el MT pipes
        for mt_item in mt_comps:
            pipe = ['no_ner', 'no_el', mt_item]
            # write the translated QALD
            write_translation(lang, pipe, pred_dir, test_name, output_dir, gold_translations, q_map)

logging.info('Formatted files generated into the directory: %s' % output_dir)
