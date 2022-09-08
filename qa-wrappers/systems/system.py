from fastapi import Request
from classy_fastapi import Routable, get
from fastapi.responses import JSONResponse

from systems.qa_utils import example_question


class QASystem(Routable):
    def __init__(self, api_url: str = None, language: str = None, kg: str = None, *args, **kwargs) -> Routable:
        super().__init__(*args, **kwargs) # initialize the APIRouter
        self.api_url = api_url
        self.language = language
        self.kg = kg

    @get("/answers", description="Get answers")
    async def get_answers(self, request: Request, question: str = example_question) -> str:
        return JSONResponse(content={"Dummy": "Dummy"})