from nllb_mt import NllbMt
from gen_huggingface_mt import GenHuggingfaceMt
import copy

class NllbPlcFtMt(GenHuggingfaceMt):
    init_kwargs = copy.deepcopy(NllbMt.init_kwargs)

    def __init__(self):
        self.init_kwargs["model_name"] = "/neamt/ft_models/nllb_mintaka_plc_final"
        self.init_kwargs["tokenizer_name"] = "/neamt/ft_models/nllb_mintaka_plc_final"
        self.init_kwargs["model_kwargs"] = {"local_files_only": True}
        self.init_kwargs["tokenizer_kwargs"] = {"local_files_only": True}
        super(NllbPlcFtMt, self).__init__(**self.init_kwargs)

