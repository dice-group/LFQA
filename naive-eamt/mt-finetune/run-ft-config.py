import sys
import json
import logging
import hf_seq2seq_mt_ft
import shutil
from pathlib import Path

"""
To run (make sure your python environment has the requirements installed):
python run-ft-config.py config/opus-ft.json
"""
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
    logging.info("Training config received: %s " % config_json)

mode = config_json.get("model_type", None)
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
    dataset_files = config_json["dataset_files_template"] % (lang)
    # Output directory to save the model
    output_dir = config_json["output_dir_template"] % lang
    intermediate_dirs.append(output_dir)
    if mode == "one2one":
        hf_seq2seq_mt_ft.fine_tune_mt_model(model_name % (src_lang, tgt_lang), tokenizer_name % (src_lang, tgt_lang), dataset_files, output_dir, False, None, src_lang, tgt_lang)
    else:
        hf_seq2seq_mt_ft.fine_tune_mt_model(model_name, tokenizer_name, dataset_files, output_dir, local_model, local_model_path, src_lang, tgt_lang)
        # set local model for the next iteration
        local_model = True
        local_model_path = output_dir
logging.info("Finished training all models")
if mode != "one2one":
    # Prepare final model
    model_dir = output_dir
    final_model = config_json["final_model"]
    # getting all the files in the source directory
    shutil.copytree(model_dir, final_model)
    # Check if intermediate models should be kept
    if not config_json.get("save_intermediate_models", True):
        for path in intermediate_dirs:
            dirpath = Path(path)
            if dirpath.exists() and dirpath.is_dir():
                shutil.rmtree(dirpath)
    logging.info("Final model available at: %s" % final_model)