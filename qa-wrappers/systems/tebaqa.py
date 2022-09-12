from fastapi import Request
from fastapi.responses import JSONResponse
from classy_fastapi import get, post

import requests
import logging
import json

from systems.system import QASystem
from systems.qa_utils import example_question, parse_gerbil, dummy_answers


logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

class TeBaQA(QASystem):
    @get("/answers", description="Get answers")
    async def get_answers(self, question: str = example_question) -> str:
        query_data = {'query': question, 'lang': self.language}

        logger.info('Get answers from TeBaQA: {0}'.format(str(query_data)))

        response = requests.post(self.api_url, query_data).json()
        final_response = {'answer': response['answers'], 'SPARQL': response['sparql']} # preparation of the final response TODO: unify with other systems
        return JSONResponse(content=final_response)

    @get("/answers_raw", description="Get answers raw")
    async def get_answers_raw(self, question: str = example_question) -> str:
        query_data = {'query': question, 'lang': self.language}

        logger.info('Get raw answers from TeBaQA: {0}'.format(str(query_data)))

        response = requests.post(self.api_url, query_data).json()
        final_response = response
        return JSONResponse(content=final_response)

    @post("/gerbil", description="Get gerbil response")
    async def gerbil_response(self, request: Request) -> str:
        try:
            request_body = str(await request.body())
            question, lang = parse_gerbil(request_body) # get question and language from the gerbil request
            
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