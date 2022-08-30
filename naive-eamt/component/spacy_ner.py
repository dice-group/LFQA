# This class demonstrates how each component should look like
import logging
import spacy
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/util/')
import common_util as c_util


class SpacyNer:
    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        # Load NER model
        # load the NER tagger
        self.nlp = spacy.load("xx_ent_wiki_sm")
        logging.debug('SpacyNer component initialized.')

    def process_input(self, query):
        '''
        Function to annotate entities in a give natural language text.

        :param query: natural language text to be annotated
        :return:  formatted dictionary as stated in the README for NER output
        '''
        logging.debug('Input received: %s' % query)
        ent_indexes = []
        # run NER over sentence
        doc = self.nlp(query)
        logging.debug('spacy annotation: %s' % doc)
        # find the start and end indexes
        if doc.ents:
            for ent in doc.ents:
                new_item = {
                    'surface_form': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                }
                ent_indexes.append(new_item)
        output = {
            'text': query,
            'lang': c_util.detect_lang(query),
            'ent_mentions': ent_indexes
        }
        logging.debug('Output: %s' % output)
        return output
