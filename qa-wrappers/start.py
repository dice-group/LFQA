"""
This is the main entry point for the QA Wrappers application.

Here we parse the config file and include the routers for each system.
"""

from imp import reload
from fastapi import FastAPI
from configparser import ConfigParser
import pathlib, os

from systems import qanswer, tebaqa, qanary


parser = ConfigParser()

with open(os.path.join(pathlib.Path(__file__).parent.resolve(), "config.ini")) as f:
    parser.read_string(f.read())

app = FastAPI(
            title=os.environ.get("APP_NAME", "QA Wrappers"),
            description=os.environ.get("APP_DESCRIPTION", "This is a QA Wrappers application."),
)

available_classes_dict = {
    "QAnswer": qanswer.QAnswer,
    "TeBaQA": tebaqa.TeBaQA,
    "Qanary": qanary.Qanary
}

for system in parser.items(): # create routers from a config file
    if system[0] != parser.default_section:
        class_name = system[0].split("_")[0]
        sys_routable = available_classes_dict[class_name](
            **dict(parser[system[0]].items()),
            prefix=f"/{system[0].lower()}",
            tags=[system[0]]
        )
        app.include_router(sys_routable.router)

@app.get("/health", include_in_schema=False)
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)