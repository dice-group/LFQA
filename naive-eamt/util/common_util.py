import fasttext
import logging
# only works inside docker
model = fasttext.load_model("/neamt/data/lid.176.ftz")


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
    # TODO: Implement this function
    pass
# method to divide incoming string into sentences
def split_sentences(query):
    # TODO: Implement this function
    pass