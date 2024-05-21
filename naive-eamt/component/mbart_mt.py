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
            'en': 'en_XX',  # English
            'de': 'de_DE',  # German
            'ru': 'ru_RU',  # Russian
            'fr': 'fr_XX',  # French
            'es': 'es_XX',  # Spanish
            'pt': 'pt_XX',  # Portuguese
            'it': 'it_IT',  # Italian
            'nl': 'nl_XX',  # Dutch
            'uk': 'uk_UA',  # Ukrainian
            'zh': 'zh_CN',  # Chinese
            'ja': 'ja_XX',  # Japanese
            'lt': 'lt_LT',  # Lithuanian
            'hi': 'hi_IN',  # Hindi
            'id': 'id_ID',  # Indonesian
            'ko': 'ko_KR',  # Korean
            'af': 'af_ZA',  # Afrikaans
            'bn': 'bn_IN',  # Bengali
            'ur': 'ur_PK',  # Urdu
            'et': 'et_EE',  # Estonian
            'he': 'he_IL',  # Hebrew
            'lv': 'lv_LV',  # Latvian
            'ro': 'ro_RO',  # Romanian
            'th': 'th_TH',  # Thai
            'cs': 'cs_CZ',  # Czech
            'fi': 'fi_FI',  # Finnish
            'pl': 'pl_PL',  # Polish
            'sv': 'sv_SE',  # Swedish
            'tr': 'tr_TR',  # Turkish
            'ar': 'ar_AR',  # Arabic
            'az': 'az_AZ',  # Azerbaijani
            'gu': 'gu_IN',  # Gujarati
            'km': 'km_KH',  # Khmer
            'kn': 'kn_IN',  # Kannada
            'kk': 'kk_KZ',  # Kazakh
            'ml': 'ml_IN',  # Malayalam
            'mr': 'mr_IN',  # Marathi
            'mn': 'mn_MN',  # Mongolian
            'ne': 'ne_NP',  # Nepali
            'fa': 'fa_IR',  # Persian
            'ps': 'ps_AF',  # Pashto
            'si': 'si_LK',  # Sinhala
            'sw': 'sw_KE',  # Swahili
            'ta': 'ta_IN',  # Tamil
            'te': 'te_IN',  # Telugu
            'tl': 'tl_XX',  # Tagalog
            'vi': 'vi_VN',  # Vietnamese
            'xh': 'xh_ZA',  # Xhosa
            'gl': 'gl_ES',  # Galician
            'sl': 'sl_SI',  # Slovene
            'hr': 'hr_HR',  # Croatian
            'ka': 'ka_GE',  # Georgian
            'mk': 'mk_MK',  # Macedonian
            'my': 'my_MM'   # Burmese
        }
    }

    def __init__(self):
        super(MbartMt, self).__init__(**self.init_kwargs)
