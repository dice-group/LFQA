# Imports
from evaluate import load
import logging
from flask import request
# importing the flask Module
from flask import Flask

# Configuring logging
logging.basicConfig(filename='/bertscore/logs/bertscore.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logging.info('Loading bertscore model..')

bertscore = load("bertscore")
# Execute sample computation to initialize the model
predictions = ["hi there", "mister kenobi"]
references = ["hello there", "general kenobi"]
results = bertscore.compute(predictions=predictions, references=references, lang="en")
logging.debug('Sample result: %s' % str(results))

logging.info('Model loaded')

app = Flask(__name__)

# Service
@app.route('/', methods=['GET','POST'])
def check_service():
    return 'BERT-Score service is active', 200

# Service
@app.route('/bertscore', methods=['POST'])
def get_bertscore():
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
        results = bertscore.compute(predictions=pred_arr, references=ref_arr, lang=lang)
        logging.debug('Generated metrics: %s' % results)
        return results
    else:
        return f'Invalid request', 400