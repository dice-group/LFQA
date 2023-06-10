# This class demonstrates how each component should look like
import logging
import threading
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import threadsafe_resource_pool_util as trp_util
from ner_abs import GenNER

def fetch_ent_indexes(ner_results, query):
    '''
    Function to fetch the start and end indexes of each entity.

    :param ner_results: Annotated NER results from huggingface/babescape NER pipeline
    :param query: query to be annotated
    :return: entity mentions along with their surface forms and start/end indexes
    '''
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
            # condition involving I but no B before
            if not ('start' in ent_item):
                ent_item['start'] = entry['start']
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


class GenHuggingfaceNer(GenNER):
    def __init__(self, tokenizer_name, model_name):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Load NER model
        # self.ner_tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.tokenizer_name = tokenizer_name
        self.ner_model = AutoModelForTokenClassification.from_pretrained(model_name)
        """
        Huggingface's tokenizers have an issue with parallel thread access (https://github.com/huggingface/tokenizers/issues/537).
        """
        self.NLP = {}
        def nlp_gen():
            ner_tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
            nlp = pipeline("ner", model=self.ner_model, tokenizer=ner_tokenizer)
            return nlp

        self.nlp_generator = nlp_gen
        # self.nlp = pipeline("ner", model=self.ner_model, tokenizer=self.ner_tokenizer)
        logging.debug('%s component initialized.' % model_name)

    def recognize_entities(self, query, lang, extra_args):
        '''
        Function to annotate entities in a given natural language text.

        :param query: input natural language text to be annotated
        :param lang: language of the query
        
        :return:  list of entity mentions found in the provided query
        '''
        nlp = trp_util.get_threadsafe_object(type(self).__name__, self.nlp_generator)
        try:
            # Get thread safe NLP/tokenizer
            ner_results = nlp(query)
            logging.debug(ner_results)
            # find the start and end indexes
            ent_indexes = fetch_ent_indexes(ner_results, query)
            return ent_indexes
        finally:
            trp_util.release_threadsafe_object(type(self).__name__, nlp)
