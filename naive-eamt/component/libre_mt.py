# This class demonstrates how each component should look like
import logging

import requests

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import placeholder_util as p_util


def fetch_translation(query_plc, source_lang, url):
    req_json = {
        'q': query_plc,
        'source': source_lang,
        'target': 'en'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=req_json)

    trans_text = response.json()['translatedText']
    return trans_text


class LibreMt:
    sample_var = None

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.url = "http://libremt:5000/translate"
        logging.debug('LibreMt component initialized.')

    def process_input(input):
        """
        Each class must have process_input function. 
        Depending upon the type of the component, it should expect/verify a certain input format.
        The output should always be formatted as per the requirements as well. 
        The input and output format for different component types can be found in the main readme file.
        """
        # Send input for processing to the placeholder util
        input = p_util.put_placeholders(input)
        # acquire text translated to English
        trans_text = fetch_translation(input['text_plc'], input['lang'], 'en')
        # replace placeholders in the translated text
        trans_text = p_util.replace_placeholders(trans_text, input)
        return trans_text
