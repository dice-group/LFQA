from gen_huggingface_mt import GenHuggingfaceMt


class NllbMt(GenHuggingfaceMt):
    init_kwargs = {
        "model_name": "facebook/nllb-200-distilled-600M",
        "tokenizer_name": "facebook/nllb-200-distilled-600M",
        "model_kwargs": {},
        "tokenizer_kwargs": {},
        # https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
        # https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200
        "lang_code_map": {
            'en': 'eng_Latn', # English
            'de': 'deu_Latn', # German
            'ru': 'rus_Cyrl', # Russian
            'fr': 'fra_Latn', # French
            'es': 'spa_Latn', # Spanish
            'pt': 'por_Latn', # Portuguese
            'it': 'ita_Latn', # Italian
            'nl': 'nld_Latn', # Dutch
            'uk': 'ukr_Cyrl', # Ukranian
            'be': 'bel_Cyrl', # Belarusian
            'zh': 'zho_Hans', # Chinese
            'ja': 'jpn_Jpan', # Japanese
            'ba': 'bak_Cyrl', # Bashkir
            'lt': 'lit_Latn', # Lithuanian
            'hy': 'hye_Armn', # Armenian
            'hi': 'hin_Deva', # Hindi
            'id': 'ind_Latn', # Indonesian
            'ko': 'kor_Hang', # Korean
            'af': 'afr_Latn', # Afrikaans
            'arb': 'arb_Arab', # Modern Standard Arabic
            'bn': 'ben_Beng', # Bengali
            'pbt': 'pbt_Arab', # Southern Pashto
            'ca': 'cat_Latn', # Catalan
            'da': 'dan_Latn', # Danish
            'ga': 'gle_Latn', # Irish
            'km': 'khm_Khmr', # Khmer
            'et': 'est_Latn', # Estonian
            'he': 'heb_Hebr', # Hebrew
            'lv': 'lvs_Latn', # Latvian
            'ro': 'ron_Latn', # Romanian
            'th': 'tha_Thai', # Thai
        }
    }

    def __init__(self):
        super(NllbMt, self).__init__(**self.init_kwargs)
