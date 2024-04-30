from gen_huggingface_mt import GenHuggingfaceMt


class MbartMt(GenHuggingfaceMt):
    init_kwargs = {
        "model_name": "facebook/mbart-large-50-many-to-many-mmt",
        "tokenizer_name": "facebook/mbart-large-50-many-to-many-mmt",
        "model_kwargs": {},
        "tokenizer_kwargs": {},
        # https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
        # https://huggingface.co/facebook/mbart-large-50#languages-covered
        "lang_code_map": {
            'en': 'en_XX', # English
            'de': 'de_DE', # German
            'ru': 'ru_RU', # Russian
            'fr': 'fr_XX', # French
            'es': 'es_XX', # Spanish
            'pt': 'pt_XX', # Portuguese
            'it': 'it_IT', # Italian
            'nl': 'nl_XX', # Dutch
            'uk': 'uk_UA', # Ukranian
            'zh': 'zh_CN', # Chinese
            'ja': 'ja_XX', # Japanese
            'lt': 'lt_LT', # Lithuanian
            'hi': 'hi_IN', # Hindi
            'id': 'id_ID', # Indonesian
            'ko': 'ko_KR', # Korean
            'af': 'af_ZA', # Afrikaans
            'bn': 'bn_IN', # Bengali
            'ur': 'ur_PK', # Urdu
            'pbt': 'ps_AF', # Southern Pashto
            'et': 'et_EE', # Estonian
            'he': 'he_IL', # Hebrew
            'lv': 'lv_LV', # Latvian
            'ro': 'ro_RO', # Romanian
            'th': 'th_TH', # Thai
        }
    }

    def __init__(self):
        super(MbartMt, self).__init__(**self.init_kwargs)
