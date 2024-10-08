from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import cache_util

class GenEL(ABC):
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
        logging.debug('Input received at %s: %s' % (type(self).__name__, input))
        query = input['text']
        lang = input['lang']
        # run the preprocessing function
        extra_args = self.prep_input_args(input)
        # cast the indexes for integers
        ent_indexes = input.get('ent_mentions', [])
        for mention in ent_indexes:
            mention['start'] = int(mention['start'])
            mention['end'] = int(mention['end'])
        # find the entity links
        input['ent_mentions'] = cache_util.call(self.link_entities, self.__class__.__qualname__, query, lang, ent_indexes, extra_args)
        logging.debug('Output: %s' % input)
