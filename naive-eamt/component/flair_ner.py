# This class demonstrates how each component should look like
import logging

from flair.data import Sentence
from flair.models import SequenceTagger

import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util


class FlairNer:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Load NER model
        # load the NER tagger
        self.tagger = SequenceTagger.load('flair/ner-multi')
        logging.debug('FlairNer component initialized.')

    def process_input(self, query):
        '''
        Function to annotate entities in a give natural language text.

        :param query: natural language text to be annotated
        :return:  formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % query)
        ent_indexes = []
        # make a sentence
        sentence = Sentence(query)
        # run NER over sentence
        self.tagger.predict(sentence)
        logging.debug('flair annotation: %s' % sentence)
        # find the start and end indexes
        for entity in sentence.get_spans('ner'):
            new_item = {
                'surface_form': entity.text,
                'start': entity.start_position,
                'end': entity.end_position
            }
            ent_indexes.append(new_item)
        output = {
            'text': query,
            'lang': c_util.detect_lang(query),
            'ent_mentions': ent_indexes
        }
        logging.debug('Output: %s' % output)
        return output
