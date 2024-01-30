from gen_huggingface_mt import GenHuggingfaceMt


class NllbMt(GenHuggingfaceMt):
    init_kwargs = {
        "model_name": "facebook/nllb-200-distilled-600M",
        "tokenizer_name": "facebook/nllb-200-distilled-600M",
        "model_kwargs": {},
        "tokenizer_kwargs": {},
        # https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200
        "lang_code_map": {
            'en': 'eng_Latn',
            'de': 'deu_Latn',
            'ru': 'rus_Cyrl',
            'fr': 'fra_Latn',
            'es': 'spa_Latn',
            'pt': 'por_Latn',
            'it': 'ita_Latn',
            'nl': 'nld_Latn',
            'uk': 'ukr_Cyrl',
            'be': 'bel_Cyrl',
            'zh': 'zho_Hans',
            'ja': 'jpn_Jpan',
            'ba': 'bak_Cyrl',
            'lt': 'lit_Latn',
            'hy': 'hye_Armn'
        }
    }

    def __init__(self):
        super(NllbMt, self).__init__(**self.init_kwargs)
