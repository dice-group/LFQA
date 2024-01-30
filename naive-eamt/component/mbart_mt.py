from gen_huggingface_mt import GenHuggingfaceMt


class MbartMt(GenHuggingfaceMt):
    init_kwargs = {
        "model_name": "facebook/mbart-large-50-many-to-many-mmt",
        "tokenizer_name": "facebook/mbart-large-50-many-to-many-mmt",
        "model_kwargs": {},
        "tokenizer_kwargs": {},
        # https://huggingface.co/facebook/mbart-large-50#languages-covered
        "lang_code_map": {
            'en': 'en_XX',
            'de': 'de_DE',
            'ru': 'ru_RU',
            'fr': 'fr_XX',
            'es': 'es_XX',
            'pt': 'pt_XX',
            'it': 'it_IT',
            'nl': 'nl_XX',
            'uk': 'uk_UA',
            'zh': 'zh_CN',
            'ja': 'ja_XX',
            'lt': 'lt_LT'
        }
    }

    def __init__(self):
        super(MbartMt, self).__init__(**self.init_kwargs)
