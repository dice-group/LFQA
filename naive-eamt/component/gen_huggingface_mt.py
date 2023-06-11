# This class demonstrates how each component should look like
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import threading
from mt_abs import GenMT
import sys
sys.path.insert(1, '/neamt/util/')
import threadsafe_resource_pool_util as trp_util
class GenHuggingfaceMt(GenMT):
    def __init__(self, model_name, tokenizer_name, model_kwargs, tokenizer_kwargs, lang_code_map):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Only accessible inside the docker network
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **model_kwargs)
        # self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **tokenizer_kwargs)
        self.tokenizer_name = tokenizer_name
        self.tokenizer_kwargs = tokenizer_kwargs
        self.lang_code_map = lang_code_map

        """
        Huggingface's tokenizers have an issue with parallel thread access (https://github.com/huggingface/tokenizers/issues/537). 
        """
        def tokenizer_gen():
            return AutoTokenizer.from_pretrained(self.tokenizer_name, **self.tokenizer_kwargs)

        self.tokenizer_generator = tokenizer_gen

        logging.debug('%s component initialized.' % type(self).__name__)


    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        # Get thread safe tokenizer
        tokenizer = trp_util.get_threadsafe_object(type(self).__name__, self.tokenizer_generator)
        try:
            tokenizer.src_lang = self.lang_code_map[source_lang]
            encoded_ar = tokenizer(trans_text, return_tensors="pt")
            generated_tokens = self.model.generate(
                **encoded_ar,
                forced_bos_token_id=tokenizer.lang_code_to_id[self.lang_code_map[target_lang]]
            )
            trans_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            return trans_text
        finally:
            trp_util.release_threadsafe_object(type(self).__name__, tokenizer)
