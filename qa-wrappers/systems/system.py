from fastapi import Request
from classy_fastapi import Routable, get
from fastapi.responses import JSONResponse

from systems.qa_utils import example_question


class QASystem(Routable):
    """
    This is the base class for all QA systems.

    It inherits from the Routable class of the classy_fastapi package which allows us to create the methods wrapped as the FastAPI routes.
    """
    def __init__(self, *args, **kwargs) -> Routable:
        """Constructor for the QASystem class.

        Args:
            api_url (str, optional): API URL of a QA system. Defaults to None.
            language (str, optional): Language tag of a question (ISO 639-1). Defaults to None.
            kg (str, optional): Knowledge Graph to perform the QA process on. Defaults to None.
        """
        self.api_url = kwargs.pop("api_url", None)
        self.language = kwargs.pop("language", None)
        self.kg = kwargs.pop("kg", None)
        super().__init__(*args, **kwargs) # initialize the APIRouter

    @get("/answers", description="Get answers")
    async def get_answers(self, request: Request, question: str = example_question) -> str:
        return JSONResponse(content={"Dummy": "Dummy"})