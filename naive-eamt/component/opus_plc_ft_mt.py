# This class demonstrates how each component should look like
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import threading
from mt_abs import GenMT

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

    model_tok_map = {}

    TOKENIZER = {}
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        self.lang_code_map = self.init_args["lang_code_map"]
        for lang in self.init_args["model_name_langs"]:
            model_name = self.init_args["model_name_template"] % lang
            model_kwargs = self.init_args["model_kwargs"]
            tokenizer_name = self.init_args["tokenizer_name_template"] % lang
            tokenizer_kwargs = self.init_args["tokenizer_kwargs"]
            # initializing tokenizer and model
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **model_kwargs)
            # tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **tokenizer_kwargs)
            self.model_tok_map[lang] = (model, (tokenizer_name, tokenizer_kwargs))

        logging.debug('%s component initialized.' % type(self).__name__)

    """
    Huggingface's tokenizers have an issue with parallel thread access (https://github.com/huggingface/tokenizers/issues/537).
    Implementing a workaround mentioned in: https://github.com/huggingface/tokenizers/issues/537#issuecomment-1372231603    
    """

    def get_tokenizer(self, lang):
        _id = threading.get_ident()
        tokenizer = self.TOKENIZER.get(_id, None)
        if tokenizer is None:
            tok_info = self.model_tok_map[lang][1]
            tokenizer_name = tok_info[0]
            tokenizer_kwargs = tok_info[1]
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, **tokenizer_kwargs)
            self.TOKENIZER[_id] = tokenizer
        return tokenizer

    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        # fetch model and tokenizer
        model = self.model_tok_map[source_lang][0]
        tokenizer = self.get_tokenizer(source_lang)

        tokenizer.src_lang = self.lang_code_map[source_lang]
        encoded_ar = tokenizer(trans_text, return_tensors="pt")
        generated_tokens = model.generate(**encoded_ar)
        trans_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return trans_text
