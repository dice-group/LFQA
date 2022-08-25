#!/bin/bash
PORT=$1
docker run -d \
  --name mag_es \
  -v ../mag_data/indexdbpedia_es_2016:/usr/local/tomcat/index \
  -p $PORT:8080 \
  -e AGDISTIS_NODE_TYPE=http://es.dbpedia.org/resource/ \
  -e AGDISTIS_EDGE_TYPE=http://dbpedia.org/ontology/ \
  -e AGDISTIS_BASE_URI=http://dbpedia.org \
  -e AGDISTIS_CONTEXT=False \
  -m 8G \
  --restart always\
  aksw/agdistis:latest