# This class demonstrates how each component should look like
import logging
import json
import requests
from mt_abs import GenMT

def fetch_translation(query_plc, source_lang, target_lang, url):
    '''
    Function to fetch the translation of a natural language text.

    :param target_lang: ISO code for the target language
    :param query_plc: Natural language text to be translated
    :param source_lang: ISO code for the source language
    :param url: URL of the LibreTranslate service
    :return: translated text
    '''
    req_json = {
        'source': query_plc,
        'from': source_lang,
        'to': target_lang
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(req_json))

    trans_text = response.json()['translation']
    return trans_text
class OpusMt(GenMT):
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.url = "http://opusmt:80/api/translate"
        logging.debug('OpusMt component initialized.')
    
    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        trans_text = fetch_translation(trans_text, source_lang, target_lang, self.url)
        return trans_text