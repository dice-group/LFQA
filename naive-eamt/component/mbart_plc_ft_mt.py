from mbart_mt import MbartMt
from gen_huggingface_mt import GenHuggingfaceMt
import copy


class MbartPlcFtMt(GenHuggingfaceMt):
    init_kwargs = copy.deepcopy(MbartMt.init_kwargs)

    def __init__(self):
        self.init_kwargs["model_name"] = "/neamt/ft_models/mbart50_mintaka_plc_final"
        self.init_kwargs["tokenizer_name"] = "/neamt/ft_models/mbart50_mintaka_plc_final"
        self.init_kwargs["model_kwargs"] = {"local_files_only": True}
        self.init_kwargs["tokenizer_kwargs"] = {"local_files_only": True}
        super(MbartPlcFtMt, self).__init__(**self.init_kwargs)
