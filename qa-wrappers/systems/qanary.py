from fastapi import Request
from fastapi.responses import JSONResponse
from classy_fastapi import Routable, get, post
from qanary_helpers import qanary_queries

import requests
import logging
import json

from systems.system import QASystem
from systems.qa_utils import example_question, parse_gerbil, dummy_answers


logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

class Qanary(QASystem):
    """ 
    This is the class for the Qanary QA system.

    It provides the corresponding functionality for quering the Qanary and receiving the answers.
    """
    def __init__(self, components_list: list = None, api_url: str = None, language: str = None, kg: str = None, *args, **kwargs) -> Routable:
        """Constructor for the Qanary class.

        Args:
            api_url (str, optional): API URL of a Qanary instance. Defaults to None.
            language (str, optional): Language tag of a question (ISO 639-1). Defaults to None.
            kg (str, optional): Knowledge Graph to perform the QA process on. Defaults to None.
            components_list (list, optional): list of the Qanary components to query. Defaults to None.
        """
        
        super().__init__(api_url, language, kg, *args, **kwargs)
        self.components_list = components_list

    @get("/query_candidates", description="Get query candidates")
    async def get_query_candidates(self, question: str = example_question) -> str:
        final_response = {}
        
        return JSONResponse(content=final_response)

    @get("/answers", description="Get answers")
    async def get_answers(self, question: str = example_question) -> str:
        final_response = {}
        
        return JSONResponse(content=final_response)

    @get("/answers_raw", description="Get answers raw")
    async def get_answers_raw(self, question: str = example_question) -> str:
        response = requests.post(
            url=self.api_url,
            params={
                "question": question,
                "componentlist[]": self.components_list,
            }
        ).json()
        return JSONResponse(content=response)

    @post("/gerbil", description="Get gerbil response")
    async def gerbil_response(self, request: Request) -> str:
        try:
            request_body = str(await request.body())
            question, lang = parse_gerbil(request_body) # get question and language from the gerbil request
            
            logger.info('GERBIL input: {0}, {1}'.format(question, lang))
            
            response = requests.post(
                url=self.api_url,
                params={
                    "question": question,
                    "componentlist[]": self.components_list,
                }
            ).json()

            sparql = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
                PREFIX qa: <http://www.wdaqua.eu/qa#>
                SELECT DISTINCT ?v1
                FROM <{graphId}> 
                WHERE {{
                    ?s a qa:AnnotationAnswer ;
                        oa:hasBody ?body .
                    ?body rdf:value ?value .
                    ?value rdf:_1 ?v1 .
                }}
            """

            response = qanary_queries.select_from_triplestore(response["endpoint"], sparql.format(graphId=response["inGraph"]))
            
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
                    "answers": [response]
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