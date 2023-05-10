from abc import ABC, abstractmethod
import logging
import sys
import time
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import cache_util
import placeholder_util as p_util

class GenMT(ABC):

    # TODO: Need caching for 'translate_text' function, do you need to apply it for all the implementations?
    @abstractmethod
    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        raise NotImplementedError

    def prep_input_args(self, input):
        return None
    
    def process_input(self, input):
        '''
        Function to translate an entity annotated (linked) text to English

        :param input: formatted dictionary as stated in the README for EL output
        :return: translated text to English
        '''
        # Send input for processing to the placeholder util
        logging.debug('Input received: %s' % input)
        extra_args = self.prep_input_args(input)
        # Extract source and target language
        source_lang = input['lang']
        target_lang = 'en'
        if 'target_lang' in input:
            target_lang = input['target_lang']
        else:
            input['target_lang'] = target_lang

        # params for placeholder util
        query = input['text']
        plc_token = input['placeholder']
        replace_before = input['replace_before']
        kb = input.get('kb')
        ent_links = input.get('ent_mentions', [])

        # Logging start time
        start_time = time.time()
        # putting placeholders
        # input['text_plc'] = p_util.put_placeholders(query, plc_token, replace_before, target_lang, kb, ent_links)
        input['text_plc'] = cache_util.call(p_util.put_placeholders, 'put_placeholders', query, plc_token, replace_before, target_lang, kb, ent_links)
        # Logging end time
        logging.debug('Time needed to put the placeholders: %s second(s)' % ((time.time() - start_time)))

        logging.debug('Injected placeholders: %s' % input)
        # acquire text with placeholder
        trans_text = input['text_plc']

        # only translate if the source is not same as target language
        if source_lang != target_lang:
            trans_text = cache_util.call(self.translate_text, self.__class__.__qualname__, trans_text, source_lang, target_lang, extra_args)
        logging.debug('Translated text with the placeholders: %s'%trans_text)
        input['translated_text_plc'] = trans_text
        # replace placeholders in the translated text
        trans_text = p_util.replace_placeholders(trans_text, replace_before, ent_links)
        # putting trans text into the input json
        input['translated_text'] = trans_text
        logging.debug('Output: %s'%trans_text)