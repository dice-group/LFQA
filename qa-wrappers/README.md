# QA Wrappers Framework

QA Wrappers Framework helps you to build the unified web API for querying different KGQA systems.

## How to run

1. Create an `.env` file with the following variables (you can change the values):

```env
PORT=8000
APP_NAME=QA Wrappers
APP_DESCRIPTION=This is a QA Wrappers application.
```

2. Check the `config.ini` file and validate the values. The default file looks as follows:

```ini
[QAnswer]
API_URL = http://qanswer-core1.univ-st-etienne.fr/api/gerbil
Language = en
KG = dbpedia

[TeBaQA]
API_URL = https://tebaqa.demos.dice-research.org/qa-simple
Language = en
KG = dbpedia
    
[Qanary]
API_URL = http://demos.swe.htwk-leipzig.de:40111/startquestionansweringwithtextquestion
Components_List = ["NED-DBpediaSpotlight", "SINA"]
```

3. Run the application with `docker-compose build && docker-compose up -d`

## How to implement a new QA system

TBD...