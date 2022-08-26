"""
This file contains the code to start the Naïve-EAMT framework with the provided pipeline configurations.
EAMT pipelines configuration can be read/modified in the 'configuration.ini' file.
"""
# imports
import configparser
import json
from flask import request
# importing the flask Module
from flask import Flask

from component.babelscape_ner import BabelscapeNer
from component.davlan_ner import DavlanNer
from component.flair_ner import FlairNer
from component.helsinkinlp_mt import HelsinkiMt
from component.libre_mt import LibreMt
from component.mag_el import MagEl
from component.mgenre_el import MgenreEl
from component.spacy_ner import SpacyNer

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


# Initialize the requested components
detect_components('configuration.ini')


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
    return io_var


# Initiate dynamic the pipeline uris
app = Flask(__name__)


@app.route('/<string:path>', methods=['POST'])
def allow(path):
    data = request.form
    print('Query received for translation:', data)
    if (path in path_pipeline_map) and ('query' in data):
        return process_input(path, data['query'])
    else:
        return f'Invalid request'
