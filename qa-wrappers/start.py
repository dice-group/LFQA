from fastapi import FastAPI
from systems import system, qanswer, tebaqa


app = FastAPI(
            title="QA Systems Wrapper", # TODO: add environment variable
            description=""
)

system_routable = system.QASystem(
    api_url="http://localhost:8080",
    language="en",
    kg="dbpedia",
    prefix="/baseSystem",
    tags=["BaseSystem"]
)

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

app.include_router(system_routable.router)
app.include_router(qanswer_routable.router)
app.include_router(tebaqa_routable.router)

@app.get("/health", include_in_schema=False)
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)