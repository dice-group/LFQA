# BERT Similarity Docker
Docker based RESTful service that computes the [bert-score](https://huggingface.co/spaces/evaluate-metric/bertscore) and [BLEURT](https://huggingface.co/spaces/evaluate-metric/bleurt) for a given set of predictions and references.
## Docker Setup

Build the docker image:
```docker build -t bertsimilarity-neamt .``` \
Start the service use the start script:
```./start_bertsimilarity_docker.sh```\
Stop the service, use the stop script:
```./stop_bertsimilarity_docker.sh```

### Logs
The logs are maintained in the ```logs/bertsimilarity.log``` file
### Query
The BERT Similarity service can be queried through HTTP POST request, like:
```bash
curl --location --request POST 'localhost:6150/bertsimilarity' \
--header 'Content-Type: application/json' \
--data-raw '{
    "predictions": ["what'\''s your name?", "Berlin is the capital of Germany."],
    "references": ["what do people call you?", "The capital of Germany is Berlin."]
}'
```

The output would look like this:

```json
{
    "bert-score": {
        "f1": [
            0.906254768371582,
            0.9650525450706482
        ],
        "hashcode": "roberta-large_L17_no-idf_version=0.3.11(hug_trans=4.23.1)",
        "precision": [
            0.9135562181472778,
            0.9648405313491821
        ],
        "recall": [
            0.8990690112113953,
            0.9652645587921143
        ]
    },
    "bleurt": {
        "scores": [
            -0.6066297292709351,
            0.6173438429832458
        ]
    }
}
```