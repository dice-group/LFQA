# This class demonstrates how each component should look like
import logging
import os
import sys

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
# importing util (make sure to run python as module: 'python -m start.py')
# from ..util import common_util as c_util
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util

def fetch_ent_indexes(ner_results, query):
    ent_indexes = []
    ent_item = {}
    begin_detect = False
    last_entry = None
    for entry in ner_results:
        # Check for single word entity mentions
        if begin_detect and not (entry['entity'].startswith('I')):
            begin_detect = False
            ent_item['end'] = last_entry['end']
            ent_item['surface_form'] = query[ent_item['start']:ent_item['end']]
        # Check if Begin
        if entry['entity'].startswith('B'):
            ent_item = {'start': entry['start']}
            ent_indexes.append(ent_item)
            begin_detect = True
        # Check if Inside
        elif entry['entity'].startswith('I'):
            ent_item['end'] = entry['end']
            ent_item['surface_form'] = query[ent_item['start']:ent_item['end']]
            begin_detect = False
        # Ignore everything else
        else:
            ent_item = {}
        last_entry = entry
    # Check for single word entity mentions
    if begin_detect:
        ent_item['end'] = last_entry['end']
        ent_item['surface_form'] = query[ent_item['start']:ent_item['end']]
    return ent_indexes


class BabelscapeNer:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Load NER model
        self.ner_tokenizer = AutoTokenizer.from_pretrained("Babelscape/wikineural-multilingual-ner")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("Babelscape/wikineural-multilingual-ner")
        self.nlp = pipeline("ner", model=self.ner_model, tokenizer=self.ner_tokenizer)
        logging.debug('BabelScapeNER component initialized.')

    def process_input(self, query):
        """
        Each class must have process_input function. 
        Depending upon the type of the component, it should expect/verify a certain input format.
        The output should always be formatted as per the requirements as well. 
        The input and output format for different component types can be found in the main readme file.
        """
        logging.debug('Input received:', query)
        ner_results = self.nlp(query)
        print(ner_results)
        # find the start and end indexes
        ent_indexes = fetch_ent_indexes(ner_results, query)
        output = {
            'text': query,
            'lang': c_util.detect_lang(query),
            'ent_mentions': ent_indexes
        }
        logging.debug('Output:', output)
        return output
