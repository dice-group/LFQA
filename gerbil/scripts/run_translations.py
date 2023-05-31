import os
import json
import requests
import argparse

# Create the argument parser
# python run_qald_original_extended.py --system="" --dataset="" --split="" --language=""
parser = argparse.ArgumentParser(description='Process command line arguments.')

# Add the system name argument
parser.add_argument('--system', dest="system", type=str, help='the name of the system')

# Add the dataset name argument
parser.add_argument('--dataset', dest="dataset", type=str, help='the name of the dataset')

# Add the system name argument
parser.add_argument('--split', dest="split", type=str, help='the name of the split')



# Parse the command line arguments
args = parser.parse_args()

systems_dict = {
    "deeppavlov": "http://141.57.8.18:40199/deeppavlov/answer?question={question}&lang=en",
    "tebaqa": "http://141.57.8.18:40199/tebaqa/answer?question={question}&lang=en",
    "qanswer": "http://141.57.8.18:40199/qanswer/answer?question={question}&lang=en",
}

# Access the values of system and dataset
system_name = args.system
dataset_name = args.dataset
split = args.split
lang = "en" # for translations always eng

print("Executing experiments for:")
print('System Name:', system_name)
print('Dataset Name:', dataset_name)
print('Split:', split)
print('Language:', lang)

endpoint = systems_dict[system_name]
translations_path = "/data-disk2/aleksandr_ws/cikm_experiments/datasets/translated_data/translation_output_eml4u"
output_data_path = "/data-disk2/aleksandr_ws/cikm_experiments/cache/translations/{filename}.json"

translation_files = translation_files = [file for file in os.listdir(translations_path) if dataset_name in file.lower() and split in file.lower() and lang in file.lower()]

print("Translation files: ", translation_files)

## load dataset
def read_json(filename):
    with open(filename) as f:
        return json.load(f)
    
def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def extract_string_qald(json_data, language):
    for question in json_data['question']:
        if question['language'] == language:
            return question['string']

for filename in translation_files:
    questions = read_json(os.path.join(translations_path, filename))
    answers = []
    for question_obj in questions["questions"]:
        question = extract_string_qald(question_obj, lang)
        print("Question: ", question)
        
        try:
            response = requests.get(endpoint.format(question=question)).json()
        except:
            response = []

        question_obj[f"answers_pred"] = response
        answers.append(question_obj)

    write_json(answers, output_data_path.format(filename=f"{system_name}-{filename}"))