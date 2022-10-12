import json
import logging
import time
import requests
from pathlib import Path
from tqdm import tqdm

class PipelineHandler:
    
    # error count
    count = {
        'request': 0
    }
    # Read Config file
    eval_cfg = []
    # Go through the configuration to form the translation pipelines
    test_pipelines = {}
    # URL to the custom NEAMT pipeline
    url = "http://localhost:6100/custom-pipeline"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # Output directory to store the translation files to
    output_dir = 'pred_results/'
    
    def __init__(self):
        # Create the directory(s) in the output path
        print(self.output_dir)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
    def gen_pipelines(self):
        with open('eval_config.json', 'r') as ec:
            self.eval_cfg = json.load(ec)
        
        print(self.eval_cfg)
        for cfg in self.eval_cfg:
            test_name = cfg['name']
            pipes = []
            test_data = []
            if 'QALD' in test_name:
                test_data = self.get_qald_test_data(cfg['file'])
            # print data statistics
            for lang in test_data:
                print('[%s] %s language entries: %d' % (test_name, lang, len(test_data[lang])))
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
                with open(test_name + '_%s-en_gold_file.txt' % lang, 'w') as out:
                    # For each test string
                    for id in test_data[lang]:
                        out.write(test_data['en'][id] + '\n')

            self.test_pipelines[test_name] = {}
            self.test_pipelines[test_name]['pipelines'] = pipes
            self.test_pipelines[test_name]['data'] = test_data

        print('Total request count:', self.count['request'])
        
        for test in self.test_pipelines:
            print('Test Pipelines for %s:\n' % test, self.test_pipelines[test]['pipelines'])
        

    # Function to generate test data using QALD file
    def get_qald_test_data(self, filename):
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
    
    # function to create unique prediction file name
    def get_pred_file_name(self, lang, components):
        return lang + '-' + '-'.join(components)


    # Function to fetch the transation through a HTTP POST request
    def get_translation(self, query, components, error_stats):
        # print('Getting Translation for: ', query)
        payload = {
            'query': query,
            'components': ','.join(components),
            'replace_before': True
            #'placeholder': 'plc'
        }
        ret_val = ''
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=payload, timeout=600)
            # print('Translation received: ', response.text)
            if response.status_code != 200:
                print('error encountered for the query %s and components %s. Response: \n %s' % (
                    query, payload['components'], response))
                error_stats['error'] += 1
            else:
                ret_val = response.text
        except Exception as e:
            print('Following exception encountered for the query %s: %s' % (query, e))
            error_stats['exception'] += 1

        return ret_val
    # function that can be run in parallel
    def execute_pipeline(self, lang, pipeline, output_dir, test, test_data):
        print('\nProcess started: test: %s\tlang: %s\tpipeline: %s'%(test, lang, pipeline))
        error_stats = {
            'error': 0,
            'exception': 0
        }
        # Create a prediction file
        pred_file = test + '_' + self.get_pred_file_name(lang, pipeline) + '.txt'
        with open(output_dir + pred_file, 'w') as out:
            # For each test string
            for id in test_data[lang]:
                # Get the prediction
                # print('Pipeline:', pipeline)
                query = test_data[lang][id]
                out.write(self.get_translation(query, pipeline, error_stats) + '\n')
        return (len(test_data[lang]), error_stats)

    def dummy_pipeline_executor(self, lang, pipeline, output_dir, test, test_data):
        print('Process started: test: %s\tlang: %s\tpipeline: %s\tData length: %d'%(test, lang, pipeline, len(test_data[lang])))
        error_stats = {
            'error': 0,
            'exception': 0
        }
        time.sleep(2)
        return (len(test_data[lang]), error_stats)

    def thread_wrapper(self, func, args):
        return func(*args)