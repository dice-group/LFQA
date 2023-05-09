from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')

class GenEL(ABC):
    # TODO: Cache this function (maybe you need to cache all the implementations?)
    @abstractmethod
    def link_entities(self, query, lang, ent_indexes, extra_args):
        raise NotImplementedError
    def prep_input_args(self, input):
        return None
    
    def process_input(self, input):
        '''
        Function to find the links for annotated entities

        :param input: input json containing natural language text to be annotated
        :return: formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % input)
        query = input['text']
        lang = input['lang']
        # run the preprocessing function
        extra_args = self.prep_input_args(input)
        ent_indexes = input.get('ent_mentions', [])
        # find the entity links
        self.link_entities(query, lang, ent_indexes, extra_args)
        logging.debug('Output: %s' % input)