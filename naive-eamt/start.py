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
from helsinkinlp_mt import HelsinkiMt
from libre_mt import LibreMt
from mag_el import MagEl
from mgenre_el import MgenreEl
from spacy_ner import SpacyNer
# configuring logging
logging.basicConfig(filename='/neamt/logs/neamt.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# Read the configuration file and find the relevant components
comp_map = {
    'flair_ner': FlairNer,
    'spacy_ner': SpacyNer,
    'davlan_ner': DavlanNer,
    'babelscape_ner': BabelscapeNer,
    'mgenre_el': MgenreEl,
    'mag_el': MagEl,
    'libre_mt': LibreMt,
    'helsinkinlp_mt': HelsinkiMt
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

logging.info('Reading configuration file..')
# Initialize the requested components
detect_components('/neamt/configuration.ini')


# Process requests
def process_input(input_query, path):
    # Find the pipeline
    pipeline_info = path_pipeline_map[path]
    # Persist the input/output for the pipeline components
    io_var = input_query
    # Loop through pipeline components and pass it the previous output as an input
    for inst in pipeline_info['inst_list']:
        io_var = inst.process_input(io_var)
    # return the last output
    logging.info('final output:', io_var)
    return io_var


# logging.info('Started')
# Initiate dynamic the pipeline uris
app = Flask(__name__)
# logging.info('Finished')


@app.route('/<string:path>', methods=['POST'])
def allow(path):
    data = request.form
    logging.info('Query received for translation:', data)
    if (path in path_pipeline_map) and ('query' in data):
        return process_input(path, data['query'])
    else:
        return f'Invalid request'
    
# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 80))
#     app.run(use_reloader=False, host='0.0.0.0', port=port)
