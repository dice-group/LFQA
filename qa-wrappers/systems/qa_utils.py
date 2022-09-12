""" 
This file contains the functions and variables that are used by the QA wrappers in common.
"""

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