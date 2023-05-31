import json
import requests
import argparse

# Create the argument parser
# python run_qald_original_extended.py --system="" --dataset="" --language=""
parser = argparse.ArgumentParser(description='Process command line arguments.')

# Add the system name argument
parser.add_argument('--system', dest="system", type=str, help='the name of the system')

# Add the dataset name argument
parser.add_argument('--dataset', dest="dataset", type=str, help='the name of the dataset')

# Add the language argument
parser.add_argument('--language', dest="language", type=str, help='the name of the dataset')

# Parse the command line arguments
args = parser.parse_args()

# Access the values of system and dataset
system_name = args.system
dataset_name = args.dataset
lang = args.language

print("Executing experiments for:")
print('System Name:', system_name)
print('Dataset Name:', dataset_name)
print('Language:', lang)


systems_dict = {
    "deeppavlov": "http://141.57.8.18:40199/deeppavlov/answer?question={question}&lang={lang}",
    "tebaqa": "http://141.57.8.18:40199/tebaqa/answer?question={question}&lang={lang}",
    "qanswer": "http://141.57.8.18:40199/qanswer/answer?question={question}&lang={lang}",
}

datasets_dict = {
    "qald-9-plus-test-wikidata": "/data-disk2/aleksandr_ws/cikm_experiments/datasets/qald_9_plus/data/qald_9_plus_test_wikidata.json",
    "qald-9-plus-train-wikidata": "/data-disk2/aleksandr_ws/cikm_experiments/datasets/qald_9_plus/data/qald_9_plus_train_wikidata.json",
    "qald-9-plus-train-dbpedia": "/data-disk2/aleksandr_ws/cikm_experiments/datasets/qald_9_plus/data/qald_9_plus_train_dbpedia.json",
    "qald-9-plus-test-dbpedia": "/data-disk2/aleksandr_ws/cikm_experiments/datasets/qald_9_plus/data/qald_9_plus_test_dbpedia.json",
    "qald-10": "/data-disk2/aleksandr_ws/cikm_experiments/datasets/QALD-10/data/qald_10/qald_10.json",
}

output_data_path = "/data-disk2/aleksandr_ws/cikm_experiments/cache/original-{filename}.json"

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


endpoint = systems_dict[system_name]
data_path = datasets_dict[dataset_name]
        
data_json = read_json(data_path)
system_data_answers = []
for question_obj in data_json["questions"]:
    # check if such question is already there
    print("Question: ", question_obj["id"])
    question = extract_string_qald(question_obj, lang)
    
    try:
        response = requests.get(endpoint.format(question=question, lang=lang)).json()
    except:
        response = []

    question_obj[f"answers_pred"] = response
    system_data_answers.append(question_obj)
    write_json(system_data_answers, output_data_path.format(filename=f"{system_name}-{dataset_name}-{lang}"))