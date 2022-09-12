"""
This is the main entry point for the QA Wrappers application.

Here we parse the config file and include the routers for each system.
"""

from fastapi import FastAPI
from systems import qanswer, tebaqa, qanary


app = FastAPI(
            title="QA Systems Wrapper", # TODO: add environment variable
            description=""
)

# TODO: read config from file and include routers via loop

qanswer_routable = qanswer.QAnswer(
    api_url="http://qanswer-core1.univ-st-etienne.fr/api/gerbil", # TODO: diffent endpoints
    language="en",
    kg="dbpedia",
    prefix="/qanswer",
    tags=["QAnswer"]
)

tebaqa_routable = tebaqa.TeBaQA(
    api_url="https://tebaqa.demos.dice-research.org/qa-simple", # TODO: diffent endpoints
    language="en",
    kg="dbpedia",
    prefix="/tebaqa",
    tags=["TeBaQA"]
)

qanary_routable = qanary.Qanary(
    api_url="http://demos.swe.htwk-leipzig.de:40111/startquestionansweringwithtextquestion",
    components_list=["NED-DBpediaSpotlight"],
    prefix="/qanary",
    tags=["Qanary"]
)

app.include_router(qanswer_routable.router)
app.include_router(tebaqa_routable.router)
app.include_router(qanary_routable.router)

@app.get("/health", include_in_schema=False)
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)