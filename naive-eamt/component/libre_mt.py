# This class demonstrates how each component should look like
import logging
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
        'q': query_plc,
        'source': source_lang,
        'target': target_lang
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=req_json)

    trans_text = response.json()['translatedText']
    return trans_text


class LibreMt(GenMT):

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.url = "http://libretranslate:5000/translate"
        logging.debug('LibreMt component initialized.')
    
    def translate_text(self, trans_text, source_lang, target_lang):
        trans_text = fetch_translation(trans_text, source_lang, target_lang, self.url)
        return trans_text
