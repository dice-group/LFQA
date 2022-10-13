# This class demonstrates how each component should look like
import logging
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util


class EmptyNer:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        logging.debug('EmptyNer component initialized.')

    def process_input(self, input):
        '''
        Function that does not annotate any entity in a give natural language text.

        :param query: natural language text to be annotated
        :return:  formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % input)
        query = input['text']
        input['lang'] = c_util.detect_lang(query)
        input['ent_mentions'] = []
        logging.debug('Output: %s' % input)
        return input
