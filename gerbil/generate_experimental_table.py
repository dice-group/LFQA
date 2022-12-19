import json
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    return json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))

df_exp = pd.read_csv("experiments_missing_manual.log", sep="\t", header=None)
df_exp.columns = ["Annotator", "Dataset", "Language", "Experiment URI", "Time"]

exp_dict = {
    "Dataset": [],
    "Language": [],
    "System": [],
    "ExperimentURI": [],
    "MicroF1": [],
    "MacroF1": [],
    "MicroPrecision": [],
    "MacroPrecision": [],
    "MicroRecall": [],
    "MacroRecall": [],
    "QALD-F1": [],
    "Timestamp": []
}
for i,row in df_exp.iterrows():
    try:
        json_data = get_ld_json(row["Experiment URI"])['@graph'][1]
    except Exception as e:
        print("Error while parsing experiment:", row["Experiment URI"])
        continue

    exp_dict["Dataset"].append(row["Dataset"])
    exp_dict["Language"].append(row["Language"])
    exp_dict["System"].append(row["Annotator"])
    exp_dict["ExperimentURI"].append(row["Experiment URI"])
    exp_dict["MicroF1"].append(json_data['microF1'] if 'microF1' in json_data else None)
    exp_dict["MacroF1"].append(json_data['macroF1'] if 'macroF1' in json_data else None)
    exp_dict["MicroPrecision"].append(json_data['microPrecision'] if 'microPrecision' in json_data else None)
    exp_dict["MacroPrecision"].append(json_data['macroPrecision'] if 'macroPrecision' in json_data else None)
    exp_dict["MicroRecall"].append(json_data['microRecall'] if 'microRecall' in json_data else None)
    exp_dict["MacroRecall"].append(json_data['macroRecall'] if 'macroRecall' in json_data else None)
    exp_dict["QALD-F1"].append(json_data['Macro_F1_QALD'] if 'Macro_F1_QALD' in json_data else None)
    exp_dict["Timestamp"].append(row["Time"])

pd.DataFrame.from_dict(exp_dict).to_csv("results_missing_manual.csv", index=False, sep="\t")
