# This class demonstrates how each component should look like
import logging
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

from mbart_mt import MbartMt

class MbartPlcFtMt(MbartMt):
    mbart_model_name = "/neamt/ft_models/mbart50_mintaka_plc_final"
    mbart_tokenizer_name = "/neamt/ft_models/mbart50_mintaka_plc_final"
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.model = MBartForConditionalGeneration.from_pretrained(self.mbart_model_name, local_files_only=True)
        self.tokenizer = MBart50TokenizerFast.from_pretrained(self.mbart_tokenizer_name, local_files_only=True)
        self.lang_code_map = {
            'en': 'en_XX',
            'de': 'de_DE',
            'ru': 'ru_RU',
            'fr': 'fr_XX',
            'es': 'es_XX',
            'pt': 'pt_XX',
            'it': 'it_IT'
        }
        logging.debug('MbartMt (fine-tuned) component initialized.')