import json
import logging
import time
import requests
from pathlib import Path

class PipelineHandler:
    
    # error count
    count = {
        'request': 0
    }
    # Read Config file
    eval_cfg = []
    # Go through the configuration to form the translation pipelines
    test_pipelines = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # URL to the custom NEAMT pipeline
    url = None
    # Output directory to store the translation files to
    output_dir = None
    # Config file to read the pipeline config from
    config_file=None
    
    def __init__(self, url, output_dir, config_file):
        self.url = url
        self.output_dir = output_dir
        self.config_file = config_file
        # Create the directory(s) in the output path
        logging.debug(self.output_dir)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
    def gen_pipelines(self):
        with open(self.config_file, 'r') as ec:
            self.eval_cfg = json.load(ec)
        
        logging.debug(self.eval_cfg)
        for cfg in self.eval_cfg:
            test_name = cfg['name']
            pipes = []
            test_data = []
            if 'QALD' in test_name:
                test_data = self.get_qald_test_data(cfg['file'])
            elif 'MINTAKA' in test_name:
                test_data = self.get_mintaka_test_data(cfg['file'])
            # print data statistics
            for lang in test_data:
                logging.debug('[%s] %s language entries: %d' % (test_name, lang, len(test_data[lang])))
            # iterate over languages in the current config
            for lang in cfg['test_cfg']:
                ner_comps = cfg['test_cfg'][lang]['ner']
                el_comps = cfg['test_cfg'][lang]['el']
                mt_comps = cfg['test_cfg'][lang]['mt']
                lang_pipes = []
                # for each NER
                for ner_item in ner_comps:
                    # for each EL
                    for el_item in el_comps:
                        # for each MT
                        for mt_item in mt_comps:
                            lang_pipes.append([ner_item, el_item, mt_item])
                # append no_ner, no_el MT pipes
                for mt_item in mt_comps:
                    lang_pipes.append(['no_ner', 'no_el', mt_item])
                pipes.append((lang, lang_pipes))
                self.count['request'] += (len(lang_pipes) * len(test_data[lang]))
                # Write test data to a file for each lang -> en combination
                with open(self.output_dir + test_name + '_%s-en_gold_file.txt' % lang, 'w') as out:
                    # For each test string
                    for id in test_data[lang]:
                        out.write(test_data['en'][id] + '\n')

            self.test_pipelines[test_name] = {}
            self.test_pipelines[test_name]['pipelines'] = pipes
            self.test_pipelines[test_name]['data'] = test_data

        logging.debug('Total request count: %d' % self.count['request'])
        
        for test in self.test_pipelines:
            logging.debug('Test Pipelines for %s: %s\n' % (test, str(self.test_pipelines[test]['pipelines'])))
        

    # Function to generate test data using QALD file
    def get_qald_test_data(self, filename):
        """
        Generate a json with the following format:
        {
        'en': { 12: 'Who is the first person to step on the moon?', 14: 'Where is ...' ..},
        'de': {12: 'Wer ....', 14: '...'..},
        ...
        }
        """
        qald_json = {}
        res_data = {}
        with open(filename, 'r') as qald_file:
            qald_json = json.load(qald_file)
        for q_item in qald_json['questions']:
            id = q_item['id']
            for q_pair in q_item['question']:
                lang = q_pair['language']
                if lang not in res_data:
                    res_data[lang] = {}
                res_data[lang][id] = q_pair['string']
        return res_data

    def get_mintaka_test_data(self, filename):
        mintaka_json = {}
        # in mintaka english question is present separately from other languages
        res_data = { 'en': {} }
        with open(filename, 'r') as mintaka_file:
            mintaka_json = json.load(mintaka_file)
        for q_item in mintaka_json:
            id = q_item['id']
            # adding english question string
            res_data['en'][id] = q_item['question']
            for lang in q_item['translations']:
                if lang not in res_data:
                    res_data[lang] = {}
                res_data[lang][id] = q_item['translations'][lang]
        return res_data
    # function to create unique prediction file name
    def get_pred_file_name(self, lang, components):
        return lang + '-' + '-'.join(components)


    # Function to fetch the transation through a HTTP POST request
    def get_translation(self, id, lang, query, components, error_stats):
        # logging.debug('Getting Translation for: %s' % query)
        payload = {
            'query': query,
            'components': ','.join(components),
            'replace_before': False, # This should be False usually
            'full_json': True,
            'lang': lang
            #'placeholder': 'plc'
        }
        ret_val = {}
        translated_text = ''
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=payload, timeout=600)
            # logging.debug('Translation received: %s' % response.text)
            if response.status_code != 200:
                logging.debug('error encountered for the query %s and components %s. Response: \n %s' % (
                    query, payload['components'], response))
                error_stats['error'] += 1
            else:
                ret_val = response.json()
                if 'translated_text' not in ret_val:
                    # throw exception
                    raise ValueError('Received incomplete json response.')
                else:
                    translated_text = ret_val['translated_text']
                #logging.debug('Json response: %s' % ret_val)
                #logging.debug('Response type: %s' % type(ret_val))
                # Adding the ID to the answer
                ret_val['id'] = id
        except Exception as e:
            logging.debug('\nFollowing exception encountered for the payload %s: %s' % (str(payload), e))
            error_stats['exception'] += 1

        return ret_val, translated_text
    # function that can be run in parallel
    def execute_pipeline(self, lang, pipeline, test, test_data, bar_queue):
        logging.debug('\nProcess started: test: %s\tlang: %s\tpipeline: %s'%(test, lang, pipeline))
        error_stats = {
            'error': 0,
            'exception': 0
        }
        # Create a prediction file
        pred_file = self.output_dir + test + '_' + self.get_pred_file_name(lang, pipeline)
        with open(pred_file + '.txt', 'w') as out_text, open(pred_file + '.jsonl', 'w') as out_jsonl:
            # For each test string
            for id in test_data[lang]:
                # Get the prediction
                # print('Pipeline:', pipeline)
                query = test_data[lang][id]
                resp_json, translated_text = self.get_translation(id, lang, query, pipeline, error_stats)
                out_jsonl.write(str(resp_json) + '\n')
                out_text.write(translated_text + '\n')
                # Update progress bar
                bar_queue.put_nowait(1)
        return (len(test_data[lang]), error_stats)

    def dummy_pipeline_executor(self, lang, pipeline, test, test_data):
        logging.debug('Process started: test: %s\tlang: %s\tpipeline: %s\tData length: %d'%(test, lang, pipeline, len(test_data[lang])))
        error_stats = {
            'error': 0,
            'exception': 0
        }
        time.sleep(2)
        return (len(test_data[lang]), error_stats)

    def thread_wrapper(self, func, args):
        return func(*args)
