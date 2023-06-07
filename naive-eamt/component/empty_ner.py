# This class demonstrates how each component should look like
import logging
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util
from ner_abs import GenNER

class EmptyNer(GenNER):
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        logging.debug('EmptyNer component initialized.')

    def recognize_entities(self, query, lang, extra_args):
        '''
        Function to annotate entities in a given natural language text.

        :param query: input natural language text to be annotated
        :param lang: language of the query
        :param input: input json to use/provide extra information

        :return:  list of entity mentions found in the provided query
        '''
        ent_indexes = []
        # return empty entities
        return ent_indexes
