# This class demonstrates how each component should look like
from gen_huggingface_ner import GenHuggingfaceNer


class BabelscapeNer(GenHuggingfaceNer):
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        GenHuggingfaceNer.__init__(self, "Babelscape/wikineural-multilingual-ner",
                                   "Babelscape/wikineural-multilingual-ner")
