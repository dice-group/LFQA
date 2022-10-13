""" 
This file contains the functions and variables that are used by the QA wrappers in common.
"""
import re
from datetime import datetime
from pymongo import MongoClient
from SPARQLWrapper import SPARQLWrapper, JSON

example_question = "Where was Albert Einstein born?"

dummy_answers = {
    "head": {
        "link": [],
        "vars": [
            "dummy"
        ]
    },
    "results": {
        "bindings": []
    }
}

mongo_client = MongoClient('porque.cs.upb.de:27017',
    username='admin',
    password='admin',
    authSource='admin'
)

db = mongo_client.qa_systems_cache

print(db.command("serverStatus"))

def prettify_answers(answers_raw):
    if 'results' in answers_raw.keys() and len(answers_raw['results']['bindings']) > 0:
        res = list()
        for uri in answers_raw['results']['bindings']:
            res.append(uri[list(uri.keys())[0]]['value'])
        return res
    else:
        return []

def parse_gerbil(body):
    body = eval(body).decode('utf-8').split('&')
    query, lang = body[0][body[0].index('=')+1:], body[1][body[1].index('=')+1:]
    return query, lang

def execute(query: str, endpoint_url: str = 'https://dbpedia.org/sparql', agent_header: dict = {}):
    """
    https://dbpedia.org/sparql
    https://query.wikidata.org/bigdata/namespace/wdq/sparql
    """
    try:
        sparql = SPARQLWrapper(endpoint_url)
        if "wikidata" in endpoint_url:
            sparql.agent = str(agent_header)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        response = sparql.query().convert()
        return response
    except Exception as e:
        e = str(e)
        
        return {'error': e}  
    
def preprocess(question):
    return re.sub('[^A-Za-zА-Яа-яÀ-žÄäÖöÜüß0-9]+', ' ', question).lower().strip()

def cache_question(system_name: str, path: str, question: str, input_params, output):
    try:
        document = {
            'path': path,
            'question': preprocess(question),
            'raw_question': question,
            'input_params': input_params,
            'output': output,
            'date': datetime.now()
        }
        db[system_name].insert_one(document)
        print("cached:", str(document))
    except Exception as e:
        print(str(e))

def find_in_cache(system_name: str, path: str, question: str):
    try:
        result = db[system_name].find_one({'question': preprocess(question), 'path': path})
        if result:
            print("found:", str(result['output']))
            return result['output']
        else:
            return None
    except Exception as e:
        print(str(e))
        return None

    
        
