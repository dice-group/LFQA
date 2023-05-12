from mbart_mt import MbartMt
class MbartEpMt(MbartMt):
    mbart_model_name = "nikit91/mbart50_europarl_de2en_finetuned_model"
    mbart_tokenizer_name = "facebook/mbart-large-50-many-to-many-mmt"
    def __init__(self):
        MbartMt.__init__(self)