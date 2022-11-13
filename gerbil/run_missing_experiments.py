import os
import json
import time
import requests
import datetime
import pandas as pd

headers = {'Content-Type': 'multipart/form-data'}

url_postfix = """experimentData={{"type":"QA","matching":"STRONG_ENTITY_MATCH","annotator":["{annotator}"],"dataset":["{dataset}"],"answerFiles":[],"questionLanguage":"{lang}"}}"""
uploaded_dataset_prefix = "NIFDS"

data_folder = "translated_data"
files = [os.path.join(data_folder, f) for f in os.listdir("translated_data")]

df_exp = pd.read_csv("experiments.log", sep="\t", header=None)
df_exp.columns = ["Annotator", "Dataset", "Language", "Experiment URI", "Time"]

df_results = pd.read_csv("results.csv", sep="\t")

dataset_dict = {
    'English': 'en'
}

annotators = [
    'QAnswer',
    'Qanary_1',
    # 'Qanary_2',
    'Qanary_3',
    # 'Qanary_4',
    # 'Qanary_5',
]

def read_json(filename):
    with open(filename) as f:
        return json.load(f)
    
def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def upload_file(file, name, type, multiselect=None):
    files = {
        "file": (file.split("/")[-1], open(file, 'rb'), type)
    }
    data = {
        'name': name,
        'multiselect': multiselect 
    }
    request = requests.post("http://gerbil-qa.cs.uni-paderborn.de:8080/gerbil/file/upload", data=data, files=files)
    response = request.json()
    if request.status_code == 200:
        return response
    else: 
        raise Exception(f"file upload not successful: {request.status_code}: {request.content}")


if __name__ == "__main__":
    fls = [
        "QALD9PlusTrain-MT_de-flair_ner-mgenre_el-nllb_mt",
        "QALD9PlusTrain-MT_de-davlan_ner-mgenre_el-libre_mt",
        "QALD9PlusTrain-MT_de-babelscape_ner-mag_el-mbart_mt",
        "QALD9PlusTrain-MT_fr-babelscape_ner-mag_el-libre_mt",
        "QALD9Plus-MT_de-babelscape_ner-mgenre_el-opus_mt"
    ]
    # for i, row in df_results.iterrows():
    for f in fls:
        gold_standard_file = os.path.join(data_folder, f + ".json")
        gold_standard_name = f

        # if "." in str(row["MacroF1"]).replace(" ", ""):
            # print("Skip:",  gold_standard_name)
            # continue
        try:  
            upload_file(gold_standard_file, gold_standard_name, 'application/json')
        except Exception as e:
            print("Error while uploading:", gold_standard_file)
            continue

        gold_standard_file = gold_standard_file.split("/")[-1]

        for annotator_ in annotators:
            annotator = "NIFWS_{0}(http://porque.cs.upb.de:40123/{1}/gerbil)".format(annotator_, annotator_.lower())
            for src_lang, lang_code in zip(dataset_dict.keys(), dataset_dict.values()):
                
                execute_url = "http://gerbil-qa.aksw.org/gerbil/execute?" + url_postfix.format(
                    annotator=annotator,
                    dataset=f"{uploaded_dataset_prefix}_{gold_standard_name}({gold_standard_file})",
                    lang=lang_code
                )

                is_ok = False
                while not is_ok:
                    try:
                        if len(requests.get("http://gerbil-qa.aksw.org/gerbil/running").text) < 30000:
                            response = requests.get(execute_url)
                            experiment_url = "http://gerbil-qa.aksw.org/gerbil/experiment?id={0}".format(response.text)
                            c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            print(f"{annotator}\t{gold_standard_name}\t{src_lang}\t{experiment_url}\t{c_time}\n")
                            
                            with open("experiments_missing_manual.log", 'a') as f:
                                f.write(f"{annotator}\t{gold_standard_name}\t{src_lang}\t{experiment_url}\t{c_time}\n")

                            is_ok = True
                        else:
                            time.sleep(60)
                        
                    except:
                        time.sleep(60)
