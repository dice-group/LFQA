# This class demonstrates how each component should look like
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import placeholder_util as p_util


class NllbMt:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
        self.lang_code_map = {
            'en': 'eng_Latn',
            'de': 'deu_Latn',
            'ru': 'rus_Cyrl',
            'fr': 'fra_Latn',
            'es': 'spa_Latn',
            'pt': 'por_Latn'
        }
        logging.debug('NllbMt component initialized.')

    def process_input(self, input):
        '''
        Function to translate an entity annotated (linked) text to English

        :param input: formatted dictionary as stated in the README for EL output
        :return: translated text to English
        '''
        # Send input for processing to the placeholder util
        logging.debug('Input received: %s' % input)
        input = p_util.put_placeholders(input)
        # acquire text translated to English
        trans_text = input['text_plc']
        # only translate if the source is non-english
        if input['lang'] != 'en':
            self.tokenizer.src_lang = self.lang_code_map[input['lang']]
            encoded_ar = self.tokenizer(input['text_plc'], return_tensors="pt")
            generated_tokens = self.model.generate(
                **encoded_ar,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[self.lang_code_map['en']]
            )
            trans_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        logging.debug('Translated text with the placeholders: %s'%trans_text)
        # replace placeholders in the translated text
        trans_text = p_util.replace_placeholders(trans_text, input)
        logging.debug('Output: %s'%trans_text)
        return trans_text