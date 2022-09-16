"""
This file contains the code to start the Naïve-EAMT framework with the provided pipeline configurations.
EAMT pipelines configuration can be read/modified in the 'configuration.ini' file.
"""
# imports
import configparser
import json
import logging
import os

from flask import request
# importing the flask Module
from flask import Flask
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '/neamt/component/')
from babelscape_ner import BabelscapeNer
from davlan_ner import DavlanNer
from flair_ner import FlairNer
from opus_mt import OpusMt
from libre_mt import LibreMt
from nllb_mt import NllbMt
from mbart_mt import MbartMt
from mag_el import MagEl
from mgenre_el import MgenreEl
from spacy_ner import SpacyNer
from empty_ner import EmptyNer
from empty_el import EmptyEl

# configuring logging
logging.basicConfig(filename='/neamt/logs/neamt.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# Read the configuration file and find the relevant components
comp_map = {
    'flair_ner': FlairNer,
    'spacy_ner': SpacyNer,
    'davlan_ner': DavlanNer,
    'babelscape_ner': BabelscapeNer,
    'mgenre_el': MgenreEl,
    'mag_el': MagEl,
    'libre_mt': LibreMt,
    'opus_mt': OpusMt,
    'nllb_mt': NllbMt,
    'mbart_mt': MbartMt,
    'no_ner': EmptyNer,
    'no_el': EmptyEl
}

comp_inst_map = {}
path_pipeline_map = {}


def detect_components(config_file):
    """
    Function to detect required components in the configuration files.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    for section in config:
        # Check if section is an EAMT Pipeline
        if section.strip().lower().startswith("eamt pipeline"):
            # extract pipeline name
            pipeline_name = config.get(section, 'name')
            # extract pipeline path
            pipeline_path = config.get(section, 'path')
            # extract pipeline components
            comp_list = json.loads(config.get(section, 'components'))
            # find/add components in the instance map
            inst_list = []
            for comp in comp_list:
                if comp not in comp_inst_map:
                    comp_inst_map[comp] = comp_map[comp]()
                inst_list.append(comp_inst_map[comp])
            # map the pipeline path to pipeline name + pipeline instance list
            path_pipeline_map[pipeline_path] = {
                'name': pipeline_name,
                'comp_list': comp_list,
                'inst_list': inst_list
            }
    logging.info('Paths found:%s' % path_pipeline_map)


logging.info('Reading configuration file..')
# Initialize the requested components
detect_components('/neamt/configuration.ini')


# Process requests
def process_input(input_query, path):
    # Find the pipeline
    pipeline_info = path_pipeline_map[path]
    logging.debug('Pipeline Info:\n%s' % pipeline_info)
    # Persist the input/output for the pipeline components
    io_var = input_query
    # Loop through pipeline components and pass it the previous output as an input
    for inst in pipeline_info['inst_list']:
        io_var = inst.process_input(io_var)
    # return the last output
    logging.info('final output: %s' % io_var)
    return io_var


# Process custom pipeline requests
def process_cus_input(input_query, inst_list):
    logging.debug('Pipeline Info:\n%s' % inst_list)
    # Persist the input/output for the pipeline components
    io_var = input_query
    # Loop through pipeline components and pass it the previous output as an input
    for inst in inst_list:
        io_var = inst.process_input(io_var)
    # return the last output
    logging.info('final output: %s' % io_var)
    return io_var


# logging.info('Started')
# Initiate dynamic the pipeline uris
app = Flask(__name__)


# logging.info('Finished')


@app.route('/<string:path>', methods=['POST'])
def gen_pipe(path):
    data = request.form
    logging.info('Query received at path: %s' % path)
    logging.info('Query received for translation: %s' % data['query'])

    if (path in path_pipeline_map) and ('query' in data):
        # Temporary workaround for placeholder, removing '?' from query
        logging.debug('Input query: %s' % data['query'])
        san_query = data['query'].replace('?', '')
        logging.debug('Sanitized input query: %s' % san_query)
        return process_input(data['query'], path)
    else:
        return f'Invalid request'


@app.route('/custom-pipeline', methods=['POST'])
def cus_pipe():
    data = request.form
    logging.info('Query received at custom-pipeline')
    logging.info('Data received for translation: %s' % data)
    comp_arr = data['components'].split(',')
    inst_list = []
    for item in comp_arr:
        inst_list.append(comp_inst_map[item.strip()])

    if (len(inst_list) == len(comp_arr)) and ('query' in data):
        # Temporary workaround for placeholder, removing '?' from query
        logging.debug('Input query: %s' % data['query'])
        san_query = data['query'].replace('?', '')
        logging.debug('Sanitized input query: %s' % san_query)
        return process_cus_input(san_query, inst_list)
    else:
        return f'Invalid request'

# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 80))
#     app.run(use_reloader=False, host='0.0.0.0', port=port)
