""" 
This file contains the functions and variables that are used by the QA wrappers in common.
"""
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

def execute(query: str, endpoint_url: str = 'https://dbpedia.org/sparql'):
    """
    https://dbpedia.org/sparql
    https://query.wikidata.org/bigdata/namespace/wdq/sparql
    """
    agent_header = {'User-Agent': 'wiki_parser_online/0.17.1 (https://deeppavlov.ai;'
                                        ' info@deeppavlov.ai) deeppavlov/0.17.1'}
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
