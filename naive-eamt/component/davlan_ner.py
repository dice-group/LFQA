# This class demonstrates how each component should look like
from gen_huggingface_ner import GenHuggingfaceNer


class DavlanNer(GenHuggingfaceNer):
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        GenHuggingfaceNer.__init__(self, "Davlan/bert-base-multilingual-cased-ner-hrl",
                                   "Davlan/bert-base-multilingual-cased-ner-hrl")
