from fastapi import Request
from fastapi.responses import JSONResponse
from classy_fastapi import get, post

import requests
import logging
import json

from systems.system import QASystem
from systems.qa_utils import example_question, prettify_answers, parse_gerbil, dummy_answers, execute


logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

class QAnswer(QASystem):
    """ 
    This is the class for the QAnswer QA system.

    It provides the wrapper functionality for the QAnswer QA system.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kg == 'dbpedia':
            self.endpoint_url = 'https://dbpedia.org/sparql'
        elif self.kg == 'wikidata':
            self.endpoint_url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'

    @get("/query_candidates", description="Get query candidates")
    async def get_query_candidates(self, question: str = example_question) -> str:
        response = requests.get(
            self.api_url.format(question=question, lang=self.language, kb=self.kg)
        ).json()
        final_response = {'queries': [q['query'] for q in response['queries']]}
        
        return JSONResponse(content=final_response)

    @get("/answers", description="Get answers")
    async def get_answers(self, question: str = example_question) -> str:
        query_data = {'query': question, 'lang': self.language, 'kb': self.kg}

        logger.info("Asking QAnswer: {0}".format(str(query_data)))

        response = requests.post(self.api_url, query_data).json()['questions'][0]['question'] # query to QAnswer
        # preparation of the final response TODO: unify with other systems
        final_response = { 'answer': None, 'answers_raw': None, 'SPARQL': None, 'confidence': None}
        final_response['answers_raw'] = json.loads(response['answers'])
        final_response['answer'] = prettify_answers(final_response['answers_raw'])
        final_response['SPARQL'] = response['language'][0]['SPARQL']
        final_response['confidence'] = response['language'][0]['confidence']
        
        return JSONResponse(content=final_response)

    @get("/answers_raw", description="Get answers raw")
    async def get_answers_raw(self, question: str = example_question) -> str:
        query_data = {'query': question, 'lang': self.language, 'kb': self.kg}
        response = requests.post(self.api_url, query_data).json() # query to QAnswer
        return JSONResponse(content=response)

    @post("/gerbil", description="Get gerbil response")
    async def gerbil_response(self, request: Request) -> str:
        try:
            request_body = str(await request.body())
            question, lang = parse_gerbil(request_body) # get question and language from the gerbil request
            
            logger.info('GERBIL input: {0} {1}'.format(question, lang))
            
            query_data = {'question': question, 'lang': lang, 'kb': self.kg} 
            response = requests.get(self.api_url, params=query_data).json() # ?question=test&lang=en&kb=dbpedia&user=open
            first_query = response["queries"][0]['query']

            final_response = {
                "questions": [{
                    "id": "1",
                    "question": [{
                        "language": lang,
                        "string": question
                    }],
                    "query": {
                        "sparql": ""
                    },
                    "answers": [execute(first_query, self.endpoint_url)]   
                }]
            }
        except Exception as e:
            logger.error("Error in QAnswer.gerbil_response: {0}".format(str(e)))
            final_response = {
                "questions": [{
                    "id": "1",
                    "question": [{
                        "language": lang,
                        "string": question
                    }],
                    "query": {
                        "sparql": ""
                    },
                    "answers": [dummy_answers]   
                }]
            }
            
        return JSONResponse(content=final_response)