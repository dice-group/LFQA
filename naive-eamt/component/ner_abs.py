from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util

class GenNER(ABC):
    # TODO: Cache this function (maybe you need to cache all the implementations?)
    @abstractmethod
    def recognize_entities(self, query, lang, extra_args):
        raise NotImplementedError
    def prep_input_args(self, input):
        return None
    
    def process_input(self, input):
        '''
        Function to annotate entities in a give natural language text.

        :param input: input json containing natural language text to be annotated
        :return:  formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % input)
        query = input['text']
        if 'lang' in input:
            lang = input['lang']
        else:
            lang = c_util.detect_lang(query)
            input['lang'] = lang
        # run the preprocessing function
        extra_args = self.prep_input_args(input)
        # find the entity mentions
        ent_indexes = self.recognize_entities(query, lang, extra_args)
        input['ent_mentions'] = ent_indexes
        logging.debug('Output: %s' % input)