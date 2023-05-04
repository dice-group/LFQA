# This script is to help generate the translations for the defined test configuration
import sys
import json
import logging
import time
import requests
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing as mp
from pipeline_handler import PipelineHandler

'''
Example usage:
python run_test.py  "http://xyz:6100/custom-pipeline" "translation_output/" "config/eval_config.json" 6
'''

args = sys.argv[1:]
# Default values
# URL to the custom NEAMT pipeline
url = "http://localhost:6100/custom-pipeline"
# Output directory to store the translation files to
output_dir = "pred_results/"
# Config file to read the pipeline config from
config_file = 'config/eval_config.json'
# Number of processes to spawn
num_procs = 5

if len(args) == 4:
    url = args[0]
    output_dir = args[1]
    config_file = args[2]
    num_procs = int(args[3])


pool = Pool(processes=num_procs)
    

if __name__ == '__main__':
    
    pipe_handler = PipelineHandler(url, output_dir, config_file)
    # generate pipelines
    pipe_handler.gen_pipelines()
    # progress bar start
    # pbar = tqdm(total=pipe_handler.count['request'])
    error_stat_arr = []
    # Progress bar queue
    bar_queue = mp.Queue()
    # Function to update the progress bar
    def update_bar(q):
        pbar = tqdm(total=pipe_handler.count['request'])
        while True:
            x = q.get()
            pbar.update(x)

    # Start the progress bar as separate daemon process
    bar_process = mp.Process(target=update_bar, args=(bar_queue,), daemon=True)
    bar_process.start()
    # Callback to update error stats
    def collect_result(result):
        error_stat_arr.append(result[1])
        # print(result)
        # pbar.update(result[0])
    # multithread results arr
    proc_res_arr = []
    # Arguments array
    arg_arr = []
    # for each config
    for test in pipe_handler.test_pipelines:
        test_data = pipe_handler.test_pipelines[test]['data']
        lang_pipelines = pipe_handler.test_pipelines[test]['pipelines']
        # For each pipeline-lang pair
        for pipeline_pair in lang_pipelines:
            lang = pipeline_pair[0]
            pipelines = pipeline_pair[1]
            # for each pipeline
            for pipeline in pipelines:
                # queue pipeline execution to the pool
                proc = pool.apply_async(pipe_handler.thread_wrapper, args=(pipe_handler.execute_pipeline, [lang, pipeline, test, test_data, bar_queue]), callback=collect_result)
                proc_res_arr.append(proc)
    
    pool.close()
    [result.get() for result in proc_res_arr]
    pool.join()
    error_sum = 0
    exception_sum = 0
    for item in error_stat_arr:
        error_sum += item['error']
        exception_sum += item['exception']
    # Server errors
    print('Total error count: %d' % error_sum)
    # Exceptions in the test script
    print('Total exception count: %d' % exception_sum)
    # close progress bar
    pbar.close()
