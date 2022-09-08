from fastapi import Request
from fastapi.responses import JSONResponse
from classy_fastapi import Routable, get, post

import requests
import logging
import json

from systems.system import QASystem
from systems.qa_utils import example_question, parse_gerbil, prettify_answers


logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

class Qanary(QASystem):
    def __init__(self, components_list: list = None, api_url: str = None, language: str = None, kg: str = None, *args, **kwargs) -> Routable:
        super().__init__(api_url, language, kg, *args, **kwargs)
        self.components_list = components_list

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
        # cache request and response
        return JSONResponse(content=final_response)

    @get("/answers_raw", description="Get answers raw")
    async def get_answers_raw(self, question: str = example_question) -> str:
        query_data = {'query': question, 'lang': self.language, 'kb': self.kg}
        response = requests.post(self.api_url, query_data).json() # query to QAnswer
        return JSONResponse(content=response)

    @post("/gerbil", description="Get gerbil response")
    async def gerbil_response(self, request: Request) -> str:
        question, lang = parse_gerbil(str(await request.body())) # get question and language from the gerbil request
        
        logger.info('GERBIL input:', question, lang)
        
        query_data = {'query': question, 'lang': lang, 'kb': self.kg}
        response = requests.post(self.api_url, query_data).json()['questions'][0]['question']
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
                "answers": [json.loads(response['answers'])]   
            }]
        }

        return JSONResponse(content=final_response)