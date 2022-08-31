#!/bin/bash
PORT=$1
docker run -d \
  --name mag_fr \
  -v ../mag_data/indexdbpedia_fr_2016:/usr/local/tomcat/index \
  -p $PORT:8080 \
  -e AGDISTIS_NODE_TYPE=http://fr.dbpedia.org/resource/ \
  -e AGDISTIS_EDGE_TYPE=http://dbpedia.org/ontology/ \
  -e AGDISTIS_BASE_URI=http://dbpedia.org \
  -e AGDISTIS_CONTEXT=False \
  -m 8G \
  --restart always\
  aksw/agdistis:latest