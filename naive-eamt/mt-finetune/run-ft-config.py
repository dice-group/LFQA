import sys
import json
import logging
import hf_seq2seq_mt_ft
import shutil
import os
# Set logging format
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# get input config file
args = sys.argv[1:]
if len(args) == 1:
    config_file = str(args[0]).strip()
else:
    raise Exception("No config file provided.")
# collect args from the input config file
with open(config_file, 'r') as in_file:
    config_json = json.load(in_file)
    logging.info("Training config received:\n%s " % config_json)

model_name = config_json["model_name"]
tokenizer_name = config_json["tokenizer_name"]
lang_map = config_json["lang_map"]
local_model = False
local_model_path = None
intermediate_dirs = []
# fine-tune models iteratively in provided language sequence
for lang in config_json["lang_seq"]:
    # Source and target language, usage and encoding depends upon the model tokenizer
    src_lang = lang_map[lang]
    tgt_lang = lang_map["en"]
    # Source dataset
    dataset_file = config_json["lang_seq"]["dataset_file_template"] % lang
    # Output directory to save the model
    output_dir = config_json["lang_seq"]["output_dir_template"] % lang
    intermediate_dirs.append(intermediate_dirs)
    hf_seq2seq_mt_ft.fine_tune_mt_model(model_name, tokenizer_name, dataset_file, output_dir, local_model, local_model_path, src_lang, tgt_lang)
    # set local model for the next iteration
    local_model = True
    local_model_path = output_dir
logging.info("Finished training all models")
# Prepare final model
model_dir = output_dir
final_model = config_json["final_model"]
# getting all the files in the source directory
shutil.copytree(model_dir, final_model)
# Check if intermediate models should be kept
if not bool(config_json["save_intermediate_models"]):
    for dirpath in intermediate_dirs:
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)
logging.info("Final model available at: %s" % final_model)