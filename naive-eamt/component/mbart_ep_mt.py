from mbart_mt import MbartMt
from gen_huggingface_mt import GenHuggingfaceMt
import copy


class MbartEpMt(GenHuggingfaceMt):
    init_kwargs = copy.deepcopy(MbartMt.init_kwargs)

    def __init__(self):
        self.init_kwargs["model_name"] = "nikit91/mbart50_europarl_de2en_finetuned_model"
        self.init_kwargs["tokenizer_name"] = "facebook/mbart-large-50-many-to-many-mmt"
        super(MbartEpMt, self).__init__(**self.init_kwargs)
