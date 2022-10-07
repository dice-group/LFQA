# This class demonstrates how each component should look like
import logging
import requests
import os
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util
from ConfigParser import SafeConfigParser

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

class SwcNerEl:

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        
        parser = SafeConfigParser(os.environ)
        parser.read('/neamt/configuration.ini')
        
        section = 'SWC'

        self.url = parser.get(section, 'url')
        self.auth = parser.get(section, 'auth')
        self.pid = parser.get(section, 'pid')
        self.supported_langs = ['en', 'de']
        logging.debug('SwcNerEl component initialized.')

    def process_input(self, input):
        '''
        Function to link the entities from an annotated text.

        :param input:  formatted dictionary as stated in the README for NER output
        :return:  formatted dictionary as stated in the README for EL output
        '''
        logging.debug('Input received: %s'%input)
        query = input['text']
        input['lang'] = c_util.detect_lang(query)
        ent_indexes = []
        input['ent_mentions'] = ent_indexes
        # checking for supported languages
        if input['lang'] in self.supported_langs:
            ent_indexes.extend(fetch_entlinks(query, self.url, self.auth, self.pid))
        # set the KB to query
        input['kb'] = 'swc'
        return input
