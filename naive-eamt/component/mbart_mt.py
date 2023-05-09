# This class demonstrates how each component should look like
import logging
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

from mt_abs import GenMT

class MbartMt(GenMT):
    mbart_model_name = "facebook/mbart-large-50-many-to-many-mmt"
    mbart_tokenizer_name = "facebook/mbart-large-50-many-to-many-mmt"
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.model = MBartForConditionalGeneration.from_pretrained(self.mbart_model_name)
        self.tokenizer = MBart50TokenizerFast.from_pretrained(self.mbart_tokenizer_name)
        self.lang_code_map = {
            'en': 'en_XX',
            'de': 'de_DE',
            'ru': 'ru_RU',
            'fr': 'fr_XX',
            'es': 'es_XX',
            'pt': 'pt_XX'
        }
        logging.debug('MbartMt component initialized.')
    
    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        self.tokenizer.src_lang = self.lang_code_map[source_lang]
        encoded_ar = self.tokenizer(trans_text, return_tensors="pt")
        generated_tokens = self.model.generate(
            **encoded_ar,
            forced_bos_token_id=self.tokenizer.lang_code_to_id[self.lang_code_map[target_lang]]
        )
        trans_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return trans_text