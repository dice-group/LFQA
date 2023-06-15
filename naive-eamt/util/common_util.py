import fasttext
import logging
import spacy
from transformers import AutoTokenizer
# only works inside docker
model = fasttext.load_model("/neamt/data/lid.176.ftz")
# Spacy's multilingual Sentence boundaries model
sent_nlp = spacy.load("xx_sent_ud_sm")
# Commonly used SentencePiece based tokenizer (ref: https://huggingface.co/docs/transformers/tokenizer_summary)
sp_tokenizer = AutoTokenizer.from_pretrained("xlnet-base-cased")

def detect_lang(query):
    '''
    This function returns an ISO code for the detected language in the query text.

    :param query: natural language text
    :return: ISO language code
    '''
    logging.debug('Detecting language for query: %s'%query)
    '''model.predict function returns a nested tuple, we are choosing the language string and removing '__label__' 
    prefix from it. '''
    lang_iso_code = model.predict(query, k=1)[0][0][9:]
    return lang_iso_code


# method to tokenize string
def tokenize_query(query):
    tokens = sp_tokenizer.tokenize(query)
    return tokens


# method to divide incoming string into sentences
def split_sentences(query):
    sentences = []
    doc = sent_nlp(query)
    for sent in doc.sents:
        sentences.append(str(sent).strip())
    return sentences
