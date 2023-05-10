# This class demonstrates how each component should look like
import logging

import requests
from el_abs import GenEL

def fetch_start(elem):
    return elem['start']
def fetch_response(text, url):
    '''
    Function to fetch the entity links of an annotated natural language text.

    :param text: Annotated natural language text
    :param url: URL of the LibreTranslate service
    :return: entity links
    '''
    req_json = {
        'text': text,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=req_json)

    resp = response.json()
    return resp

class MagEl(GenEL):
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Entity Linking
        self.supported_langs = ['en', 'de', 'fr', 'es', 'it', 'ja', 'nl']
        self.endpoint_format = 'http://mag-%s:8080/AGDISTIS'
        logging.debug('MagEl component initialized.')
    def prep_input_args(self, input):
        extra_args = {}
        # Setting knowledge base as Wikidata
        input['kb'] = 'dbp'
        return None
    def link_entities(self, query, lang, ent_indexes, extra_args):
        # Check for supported languages
        if lang not in self.supported_langs:
            logging.debug('Language not supported by MAG: %s'%lang)
            return None
        endpoint = self.endpoint_format%lang
        # do not continue if non mentions are present
        if len(ent_indexes) == 0:
            logging.debug('No mentions found!')
            return None
        sentence = ''
        last_ind = 0
        # Sorting according to the start
        ent_indexes.sort(key=fetch_start)
        # Generate annotated sentence for each mention + placeholder
        for ent_mention in ent_indexes:
            cur_sent = query[last_ind:ent_mention['start']] + '<entity>' + query[ent_mention['start']:ent_mention[
                'end']] + '</entity>'
            last_ind = ent_mention['end']
            sentence += cur_sent
        sentence += query[last_ind:]
        logging.debug('Annotated sentence: %s'%sentence)
        # Step 2: Run Entity Linking on the annotated sentence(s)
        mag_resp = fetch_response(sentence, endpoint)
        # Sorting according to the start
        mag_resp.sort(key=fetch_start)
        # There's always one entry for each mention that was annotated
        logging.debug('Response from MAG: %s'%mag_resp)

        arr_ind = 0
        for item in mag_resp:
            url = item['disambiguatedURL']
            if 'notinwiki' not in url.lower():
                ent_indexes[arr_ind]['link'] = url
            arr_ind += 1

        return ent_indexes