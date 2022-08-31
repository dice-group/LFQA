# This class demonstrates how each component should look like
import logging
import json
import requests

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import placeholder_util as p_util


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
class OpusMt:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.url = "http://opusmt:80/api/translate"
        logging.debug('OpusMt component initialized.')

    def process_input(self, input):
        '''
        Function to translate an entity annotated (linked) text to English

        :param input: formatted dictionary as stated in the README for EL output
        :return: translated text to English
        '''
        # Send input for processing to the placeholder util
        logging.debug('Input received: %s' % input)
        input = p_util.put_placeholders(input)
        # acquire text translated to English
        trans_text = input['text_plc']
        # only translate if the source is non-english
        if input['lang'] != 'en':
            trans_text = fetch_translation(input['text_plc'], input['lang'], 'en', self.url)
        logging.debug('Translated text with the placeholders: %s'%trans_text)
        # replace placeholders in the translated text
        trans_text = p_util.replace_placeholders(trans_text, input)
        logging.debug('Output: %s'%trans_text)
        return trans_text