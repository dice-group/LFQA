"""
This file contains the code to start the Naïve-EAMT framework with the provided pipeline configurations.
EAMT pipelines configuration can be read/modified in the 'configuration.ini' file.
"""
# imports
import configparser, json, sys
from component.babe
# Read the configuration file and find the relevant components
comp_map = {
    'sample' : SampleComponent
}
def detect_components(config_file):
    '''
    Function to detect required components in the configuration files.
    '''
    config = configparser.ConfigParser()
    config.read(config_file)
    for section in config:
        # Check if section is an EAMT Pipeline
        if section.strip().lower().startswith("eamt pipeline"):
            # extract pipeline name
            # extract pipeline path
            # extract pipeline components
            # find/add components in the instance map
            # map the pipeline path to pipeline name + pipeline instance list
            comp_set.update(json.loads(config.get(section,'components')))
    return comp_set


# component_set = detect_components('configuration.ini')
# Initialize the requested components
# Create pipelines using end-to-end pipeline generator
# Initiate dynamic the pipeline uris
#     'flair_ner': ,
#     'spacy_ner': ,
#     'davlan_ner': ,
#     'babelscape_ner': ,
#     'mgenre_el': ,
#     'mag_el': ,
#     'libre_mt': ,
#     'helsinkinlp_mt': 