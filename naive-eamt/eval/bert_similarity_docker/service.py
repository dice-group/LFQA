import logging
from flask import request
# importing the flask Module
from flask import Flask
import model_init

# Configuring logging
logging.basicConfig(filename='/bertsimilarity/logs/bertsimilarity.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logging.info('Loading bertsimilarity models')

bertscore = model_init.bertscore
bleurt = model_init.bleurt

logging.debug('Sample bert-score result: %s' % str(model_init.bertscore_results))
logging.debug('Sample BLEURT result: %s' % str(model_init.bleurt_results))

logging.info('Models loaded')

app = Flask(__name__)

# Service
@app.route('/', methods=['GET','POST'])
def check_service():
    return 'BERT Similarity service is active', 200

# Service
@app.route('/bertsimilarity', methods=['POST'])
def get_bertsimilarity():
    global bertscore
    data = request.get_json(force=True)
    logging.debug('Data received: %s' % data)
    if ('references' in data) and ('predictions' in data):
        pred_arr = data['predictions']
        ref_arr = data['references']
        # Set language
        lang = "en"
        if 'lang' in data:
            lang = data['lang']
        # Generate results
        bertscore_results = bertscore.compute(predictions=pred_arr, references=ref_arr, lang=lang)
        if lang == "en":
            bleurt_results = bleurt.compute(predictions=pred_arr, references=ref_arr)
        else:
            bleurt_results = {'scores': [-100 for x in ref_arr]}
        res_arr = [bertscore_results, bleurt_results]
        logging.debug('Generated metrics: %s' % str(res_arr))
        return {'bert-score': bertscore_results, 'bleurt': bleurt_results}
    else:
        return f'Invalid request', 400