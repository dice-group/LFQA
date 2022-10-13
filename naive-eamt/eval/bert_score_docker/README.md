# BERT-Score Docker
Docker based RESTful service that computes the [bert-score](https://huggingface.co/spaces/evaluate-metric/bertscore) for a given set of predictions and references.
## Docker Setup

Build the docker image:
```docker build -t bertscore-neamt .``` \
Start the service use the start script:
```./start_bertscore_docker.sh```\
Stop the service, use the stop script:
```./stop_bertscore_docker.sh```

### Logs
The logs are maintained in the ```logs/bertscore.log``` file
### Query
The configured pipelines can be queried through HTTP POST request, like:
```bash
curl --location --request POST 'localhost:6150/bertscore' \
--header 'Content-Type: application/json' \
--data-raw '{
    "predictions": ["what'\''s your name?", "Berlin is the capital of Germany."],
    "references": ["what do people call you?", "The capital of Germany is Berlin."]
}'
```