import fasttext
import logging
# only works inside docker
model = fasttext.load_model("/neamt/data/lid.176.ftz")


def detect_lang(query):
    logging.debug('Detecting language for query:', query)
    '''model predict function returns a nexted tuple, we are choosing the language string and removing '__label__' 
    prefix from it. '''
    lang_iso_code = model.predict(query, k=1)[0][0][9:]
    return lang_iso_code
