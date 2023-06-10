# This class demonstrates how each component should look like
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import threading
from mt_abs import GenMT
import sys
sys.path.insert(1, '/neamt/util/')
import threadsafe_resource_pool_util as trp_util

class OpusPlcFtMt(GenMT):
    init_args = {
        "model_name_template": "/neamt/ft_models/opusmt/opusmt_mintaka_plc_%s_en",
        "tokenizer_name_template": "/neamt/ft_models/opusmt/opusmt_mintaka_plc_%s_en",
        "model_kwargs": {"local_files_only": True},
        "tokenizer_kwargs": {"local_files_only": True},
        "lang_code_map": {
            'en': 'en',
            'de': 'de',
            'fr': 'fr',
            'es': 'es',
            'it': 'it'
        },
        "model_name_langs": [ "it", "fr", "es", "de"]
    }

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        self.lang_code_map = self.init_args["lang_code_map"]
        self.model_tok_map = {}
        self.TOKENIZER = {}
        for lang in self.init_args["model_name_langs"]:
            model_name = self.init_args["model_name_template"] % lang
            model_kwargs = self.init_args["model_kwargs"]
            tokenizer_name = self.init_args["tokenizer_name_template"] % lang
            tokenizer_kwargs = self.init_args["tokenizer_kwargs"]
            # initializing tokenizer and model
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **model_kwargs)
            # tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **tokenizer_kwargs)
            """
            Huggingface's tokenizers have an issue with parallel thread access (https://github.com/huggingface/tokenizers/issues/537).
            """
            def tokenizer_gen():
                return AutoTokenizer.from_pretrained(self.tokenizer_name, **self.tokenizer_kwargs)
            bucket_name = type(self).__name__ + '_' + lang
            self.model_tok_map[lang] = (model, (bucket_name, tokenizer_gen))

        logging.debug('%s component initialized.' % type(self).__name__)


    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        model_tok_info = self.model_tok_map[source_lang]
        # fetch model and tokenizer
        model = model_tok_info[0]
        tok_info = model_tok_info[1]
        tokenizer = trp_util.get_threadsafe_object(tok_info[0], tok_info[1])
        try:
            tokenizer.src_lang = self.lang_code_map[source_lang]
            encoded_ar = tokenizer(trans_text, return_tensors="pt")
            generated_tokens = model.generate(**encoded_ar)
            trans_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            return trans_text
        finally:
            trp_util.release_threadsafe_object(tok_info[0], tokenizer)