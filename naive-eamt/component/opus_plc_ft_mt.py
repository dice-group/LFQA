# This class demonstrates how each component should look like
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

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
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        self.lang_code_map = self.init_args["lang_code_map"]
        for lang in self.lang_code_map:
            model_name = self.init_args["model_name_template"] % lang
            model_kwargs = self.init_args["model_kwargs"]
            tokenizer_name = self.init_args["tokenizer_name_template"] % lang
            tokenizer_kwargs = self.init_args["tokenizer_kwargs"]
            # initializing tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name, **model_kwargs)
            model = AutoModelForSeq2SeqLM.from_pretrained(tokenizer_name, **tokenizer_kwargs)
            self.model_tok_map[lang] = (model, tokenizer)

        logging.debug('%s component initialized.' % type(self).__name__)
    
    def translate_text(self, trans_text, source_lang, target_lang, extra_args):
        # fetch model and tokenizer
        model = self.model_tok_map[source_lang][0]
        tokenizer = self.model_tok_map[source_lang][1]

        tokenizer.src_lang = self.lang_code_map[source_lang]
        encoded_ar = tokenizer(trans_text, return_tensors="pt")
        generated_tokens = model.generate(
            **encoded_ar,
            forced_bos_token_id=tokenizer.lang_code_to_id[self.lang_code_map[target_lang]]
        )
        trans_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return trans_text