from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import cache_util
import common_util as c_util

class GenNER(ABC):
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
        logging.debug('Input received at %s: %s' % (type(self).__name__, input))
        query = input['text']
        lang = input['lang']

        # run the preprocessing function
        extra_args = self.prep_input_args(input)
        # find the entity mentions
        ent_indexes = cache_util.call(self.recognize_entities, self.__class__.__qualname__, query, lang, extra_args)
        input['ent_mentions'] = ent_indexes
        logging.debug('Output: %s' % input)