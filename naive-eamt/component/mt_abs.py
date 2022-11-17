from abc import ABC, abstractmethod
import logging
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import placeholder_util as p_util

class GenMT(ABC):
    @abstractmethod
    def translate_text(self, trans_text, source_lang, target_lang):
        pass
    
    def process_input(self, input):
        '''
        Function to translate an entity annotated (linked) text to English

        :param input: formatted dictionary as stated in the README for EL output
        :return: translated text to English
        '''
        # Send input for processing to the placeholder util
        logging.debug('Input received: %s' % input)
        input = p_util.put_placeholders(input)
        # acquire text with placeholder
        trans_text = input['text_plc']
        source_lang = input['lang']
        target_lang = 'en'
        # only translate if the source is non-english
        if source_lang != 'en':
            trans_text = self.translate_text(trans_text, source_lang, target_lang)
        logging.debug('Translated text with the placeholders: %s'%trans_text)
        # replace placeholders in the translated text
        trans_text = p_util.replace_placeholders(trans_text, input)
        logging.debug('Output: %s'%trans_text)
        return trans_text