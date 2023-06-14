#!/usr/bin/env python3
from bs4 import BeautifulSoup
import json
import logging
import requests
import time

class BENG():
    'Client for https://github.com/dice-group/BENG'
    def __init__(self, *, gerbil_url='https://beng.dice-research.org/gerbil/'):
        'Initialize the BENG client with a default or custom URL'
        self.gerbil_url = gerbil_url

    def upload_file(self, *, name, path, data):
        upload_name = requests.post(self.gerbil_url + 'file/upload', data={'name': name}, files=[('files', (name, open(path, 'rb') if path is not None else data, 'text/plain'))]).json()['files'][0]['name']
        logging.debug('Uploaded: %s', upload_name)
        return upload_name

    def execute(self, *, experiment_type='NLG', system_file=None, system_data='', dataset_file=None, dataset_data='', lang=''):
        '''Execute an experiment.
        Specify either system_file as a path to the file or system_data as a string containing the content, the same for dataset.
        Returns the experiment ID.
        '''
        system_name = 'system'
        dataset_name = 'dataset'
        system_upload = self.upload_file(name=system_name, path=system_file, data=system_data)
        dataset_upload = self.upload_file(name=dataset_name, path=dataset_file, data=dataset_data)
        data = '{"type":"' + experiment_type + '","dataset":["NIFDS_' + dataset_name + '(' + dataset_upload + ')"],"hypothesis":["HF_' + system_name + '(' + system_upload + ')"],"candidate":[],"language":"' + lang + '"}'
        r = requests.get(self.gerbil_url + 'execute', params={'experimentData': data})
        r.raise_for_status()
        return r.text

    def results(self, experiment_id):
        'Returns the experiment results, will block until the experiment is done.'
        while True:
            r = requests.get(self.gerbil_url + 'experiment', params={'id': experiment_id})
            bs = BeautifulSoup(r.text, 'html.parser')
            data = json.loads(bs.find('script', type='application/ld+json').string)
            observation = next(res for res in data['@graph'] if res['@type'] == 'qb:Observation')
            if observation['statusCode'] == '0':
                # FIXME: proper result handling, through @context?
                observation['BLEU'] = float(observation['BLEU'])
                observation['BLEU_NLTK'] = float(observation['BLEU_NLTK'])
                observation['METEOR'] = float(observation['METEOR'])
                observation['TER'] = float(observation['TER'])
                return observation
            if (warn := bs.find('span', {'class': 'gerbil-experiment-warn'})) is not None:
                logging.warn(warn.text)
            # FIXME: configurable or exponential
            time.sleep(1)
