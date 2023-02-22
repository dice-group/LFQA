from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util

class GenNER(ABC):
    @abstractmethod
    def recognize_entities(self, query, lang, input):
        pass
    
    def process_input(self, input):
        '''
        Function to annotate entities in a give natural language text.

        :param input: input json containing natural language text to be annotated
        :return:  formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % input)
        query = input['text']
        lang = c_util.detect_lang(query)
        input['lang'] = lang
        # find the entity mentions
        ent_indexes = self.recognize_entities(query, lang, input)
        input['ent_mentions'] = ent_indexes
        logging.debug('Output: %s' % input)
        return input