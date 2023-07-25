"""
This file contains the code to start the Naïve-EAMT framework with the provided pipeline configurations.
EAMT pipelines configuration can be read/modified in the 'configuration.ini' file.
"""
# imports
import configparser
import json
import logging
import os
import ast
import time

from flask import request
# importing the flask Module
from flask import Flask
import sys
import common_util as c_util

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
from swc_ner_el import SwcNerEl
from mbart_ep_mt import MbartEpMt
from mbart_plc_ft_mt import MbartPlcFtMt
from nllb_plc_ft_mt import NllbPlcFtMt
from opus_plc_ft_mt import OpusPlcFtMt

sys.path.insert(1, '/neamt/util/')
import stats_util

stat_dict = stats_util.stats
# configuring logging
logging.basicConfig(filename='/neamt/logs/neamt.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s', filemode='w')
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
    'no_el': EmptyEl,
    'swc_ner_el': SwcNerEl,
    'mbart_ep_mt': MbartEpMt,
    'mbart_plc_ft_mt': MbartPlcFtMt,
    'nllb_plc_ft_mt': NllbPlcFtMt,
    'opus_plc_ft_mt': OpusPlcFtMt
}

def_placeholder = '00'

io_exc_list = ['query', 'full_json']
comp_inst_map = {}
path_pipeline_map = {}


def detect_components(config):
    """
    Function to detect required components in the configuration files.
    """

    for section in config:
        # Check if section is an EAMT Pipeline
        if section.strip().lower().startswith("eamt pipeline"):
            # extract pipeline name
            pipeline_name = config.get(section, 'name')
            # extract pipeline path
            pipeline_path = config.get(section, 'path')
            # extract pipeline components
            comp_list = json.loads(config.get(section, 'components'))
            logging.info("list of components to be loaded: %s" % str(comp_list))
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
# Init config
config_file = '/neamt/configuration.ini'
config = configparser.ConfigParser()
config.read(config_file)
# Initialize the requested components
detect_components(config)

TOKEN_LIMIT = int(config['DEFAULT'].get('token_limit', '400'))

# Process requests
def process_input(input_query, path):
    # Find the pipeline
    pipeline_info = path_pipeline_map[path]
    return process_cus_input(input_query, pipeline_info['inst_list'])


# Process custom pipeline requests
def process_cus_input(input_query, inst_list):
    logging.debug('Pipeline Info:\n%s' % inst_list)
    # Persist the input/output for the pipeline components
    io_var = input_query
    # Check the input language
    check_lang(io_var)
    # Loop through pipeline components and pass it the previous output as an input
    for inst in inst_list:
        # Log start time
        start_time = time.time()
        inst.process_input(io_var)
        # Print step time
        logging.debug('Time needed to process input using %s class: %s second(s)' % (type(inst).__name__, (time.time() - start_time)))
    # return the last output
    logging.info('final output: %s' % io_var)
    return io_var


def check_lang(input):
    query = input['text']
    if 'lang' not in input:
        lang = c_util.detect_lang(query)
        input['lang'] = lang


# logging.info('Started')
# Initiate dynamic the pipeline uris
app = Flask(__name__)


# logging.info('Finished')

def get_input_dict(san_query, data):
    rep_before = False
    if 'replace_before' in data:
        rep_before = eval(data['replace_before'])
    placeholder = def_placeholder
    if 'placeholder' in data:
        placeholder = data['placeholder']
    f_input = {
        'text': san_query,
        'replace_before': rep_before,
        'placeholder': placeholder
    }
    # Passing on all the params that were not yet modified and are not in the exclusion list
    for entry in data:
        if (entry not in f_input) and (entry not in io_exc_list):
            f_input[entry] = data[entry]

    return f_input

def process_query(query, data, inst_list, full_json):
    # Check if query exceeds the default token length limit
    query_tokens = c_util.tokenize_query(query)
    if len(query_tokens) < TOKEN_LIMIT:
        # proceed normally
        return process_normal_query(query, data, inst_list, full_json)
    else:
        logging.info('Query length %d exceeds the default limit %d. Splitting query into smaller chunks.' % (len(query_tokens), TOKEN_LIMIT))
        # divide query into sentences
        query_sentences = c_util.split_sentences(query)
        # Form chunks of sentences combined together smaller than default token limit
        query_chunks = []
        cur_chunk = ''
        cur_chunk_len = 0
        for sentence in query_sentences:
            sentence_tokens = c_util.tokenize_query(sentence)
            # if sentence itself is bigger than token limit then create it's own chunk
            if len(sentence_tokens) > TOKEN_LIMIT:
                # flush the previous chunk to query chunks
                if cur_chunk_len > 0:
                    query_chunks.append(cur_chunk.strip())
                # add current sentence
                query_chunks.append(sentence)
                # reset current chunk
                cur_chunk = ''
                cur_chunk_len = 0
            elif len(sentence_tokens) + cur_chunk_len <= TOKEN_LIMIT:
                # add to current chunk with a whitespace
                cur_chunk += ' ' + sentence
                cur_chunk_len += len(sentence_tokens)
                # continue loop to avoid resetting cur_chunk
                continue
            else:
                query_chunks.append(cur_chunk.strip())
                # reset current chunk
                cur_chunk = sentence
                cur_chunk_len = len(sentence_tokens)
        # flush remaining chunk
        if cur_chunk_len > 0:
            query_chunks.append(cur_chunk.strip())
        # logging
        logging.info('Total %d chunks formed: %s ' % (len(query_chunks), query_chunks))
        # loop through the chunks and process them as normal query
        results = []
        for chunk in query_chunks:
            ret_val = process_normal_query(chunk, data, inst_list, full_json)
            # If the retured json is empty, something went wrong, hence stop processing and return the same
            if len(ret_val) == 0 and isinstance(ret_val, dict):
                return ret_val
            results.append(ret_val)
        # Merge the results together if they are string
        sample_res = results[0]
        if isinstance(sample_res, str):
            results = ' '.join(results)
        return results
def process_normal_query(query, data, inst_list, full_json):
    try:
        # Temporary workaround for placeholder, removing '?' from query
        logging.debug('Input query: %s' % query)
        san_query = query.replace('\n', '')
        # san_query = query.replace('?', '')
        # logging.debug('Sanitized input query: %s' % san_query)
        res = process_cus_input(get_input_dict(san_query, data), inst_list)
        if (not full_json) and ('translated_text' in res):
            return res['translated_text']
        return res
    except Exception as inst:
        logging.exception('Exception occurred for the query: %s\nException: %s' % (query, inst))
        return {}

@app.route('/<string:path>', methods=['POST'])
def gen_pipe(path):
    global stat_dict
    # incrementing query count
    stat_dict['query_count'] += 1
    data = request.form
    logging.info('Query received at path: %s' % path)
    logging.info('Query received for translation: %s' % data['query'])

    if (path in path_pipeline_map) and ('query' in data):
        # Temporary workaround for placeholder, removing '?' from query
        logging.debug('Input query: %s' % data['query'])
        san_query = data['query'].replace('?', '')
        logging.debug('Sanitized input query: %s' % san_query)
        return process_input(get_input_dict(san_query, data), path)
    else:
        return f'Invalid request'


@app.route('/custom-pipeline', methods=['POST'])
def cus_pipe():
    global stat_dict
    # incrementing query count
    stat_dict['query_count'] += 1

    #debug
    #logging.debug(request)

    if request.form:
        data = request.form
    elif request.json:
        data = request.json
    logging.info('Query received at custom-pipeline')
    logging.info('Data received for translation: %s' % data)
    comp_arr = data['components'].split(',')
    full_json = False
    if ('full_json' in data) and data['full_json']:
        full_json = True
    inst_list = []
    for item in comp_arr:
        inst_list.append(comp_inst_map[item.strip()])

    if (len(inst_list) == len(comp_arr)) and ('query' in data):
        output = None
        data_q = data['query'].strip()
        try:
            if data_q.startswith('['):
                data_q = ast.literal_eval(data_q)
        except Exception as e:
            # do nothing
            pass
        # if the query is list, then process one at a time
        if type(data_q) == list:
            logging.debug('Processing query as a list.')
            output = []
            for query in data_q:
                output.append(process_query(query, data, inst_list, full_json))
        # else process the single query
        else:
            logging.debug('Processing a single query.')
            output = process_query(data_q, data, inst_list, full_json)
        return output
    else:
        return f'Invalid request'


@app.route('/reset-stats', methods=['GET'])
def reset_stats():
    stats_util.reset_stats()
    global stat_dict
    return stat_dict


@app.route('/reset-plc-stats', methods=['GET'])
def reset_placeholder_stats():
    stats_util.reset_placeholder_stats()
    global stat_dict
    return stat_dict


@app.route('/fetch-stats', methods=['GET'])
def fetch_stats():
    global stat_dict
    return stat_dict
