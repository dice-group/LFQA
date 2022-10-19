# This class demonstrates how each component should look like
import logging
import requests
import os
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util
from configparser import SafeConfigParser
from ner_abs import GenNER

def fetch_entlinks(text, url, auth, pid):


    headers = {
      'Authorization': auth
    }

    data = {
        "numberOfConcepts": 100000,
        "numberOfTerms": 0,
        "projectId": pid,
        "language": "DE",
        "showMatchingPosition": True,
        "showMatchingDetails": True,
        "displayText": True,
        "text": text
    }


    response = requests.request("POST", url, headers=headers, params=data)
    ent_indexes = []
    if "concepts" in response.json():
        cpts = response.json()["concepts"]
        ent_indexes = []
        for c in cpts:
            if "matchingLabels" not in c:
                break
            for ml in c["matchingLabels"]:
                if "matchedTexts" not in ml:
                        break
                for mt in ml["matchedTexts"]:
                    if "positions" not in mt:
                        break
                    for pos in mt["positions"]:
                        # print(c["uri"],mt["matchedText"],pos["beginningIndex"],pos["endIndex"])
                        ent_item = {
                            "start": pos["beginningIndex"],
                            "end": pos["endIndex"],
                            "surface_form": mt["matchedText"],
                            "link": c["uri"]
                        }
                        ent_indexes.append({'': mt["matchedText"], })
    return ent_indexes

class SwcNerEl(GenNER):

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        
        parser = SafeConfigParser(os.environ)
        parser.read('/neamt/configuration.ini')
        
        section = 'SWC'

        self.url = parser.get(section, 'url').strip('"')
        self.auth = parser.get(section, 'auth').strip('"')
        self.pid = parser.get(section, 'pid').strip('"')
        self.supported_langs = ['en', 'de']
        logging.debug('SwcNerEl component initialized.')

    def recognize_entities(self, query, lang, input):
        '''
        Function to annotate entities in a given natural language text.

        :param query: input natural language text to be annotated
        :param lang: language of the query
        :param input: input json to use/provide extra information
        
        :return:  list of entity mentions found in the provided query
        '''
        ent_indexes = []
        # checking for supported languages
        if lang in self.supported_langs:
            ent_indexes.extend(fetch_entlinks(query, self.url, self.auth, self.pid))
        # set the KB to query
        input['kb'] = 'swc'
        return ent_indexes
