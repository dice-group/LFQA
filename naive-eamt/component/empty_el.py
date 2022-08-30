# This class demonstrates how each component should look like
import logging


class EmptyEl:

    def __init__(self):
        """
        Load the resources needed for your component onto the memory only in this block.
        It helps keep the framework from unnecessarily occupying the memory.
        """
        logging.debug('EmptyEl component initialized.')

    def process_input(self, input):
        '''
        Function that returns no links to the annotated input.

        :param input:  formatted dictionary as stated in the README for NER output
        :return:  formatted dictionary as stated in the README for EL output
        '''
        logging.debug('Input received: %s'%input)
        logging.debug('Output: %s'%input)
        return input
