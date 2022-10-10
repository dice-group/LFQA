# This script is to help generate the translations for the defined test configuration
import json
import logging
import time
import requests
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
from pipeline_handler import PipelineHandler

pool = Pool(processes=5)
    

if __name__ == '__main__':
    
    pipe_handler = PipelineHandler()
    # generate pipelines
    pipe_handler.gen_pipelines()
    # progress bar start
    pbar = tqdm(total=pipe_handler.count['request'])
    error_stat_arr = []
    # Callback to update pbar
    def collect_result(result):
        error_stat_arr.append(result[1])
        # print(result)
        pbar.update(result[0])
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
                proc = pool.apply_async(pipe_handler.thread_wrapper, args=(pipe_handler.execute_pipeline, [lang, pipeline, pipe_handler.output_dir, test, test_data]), callback=collect_result)
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
