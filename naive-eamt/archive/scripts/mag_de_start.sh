#!/bin/bash
PORT=$1
docker run -d \
  --name mag_de \
  -v ../mag_data/indexdbpedia_de_2016:/usr/local/tomcat/index \
  -v ../mag_data/index_bycontext_de:/usr/local/tomcat/index_bycontext \
  -p $PORT:8080 \
  -e AGDISTIS_NODE_TYPE=http://de.dbpedia.org/resource/ \
  -e AGDISTIS_EDGE_TYPE=http://dbpedia.org/ontology/ \
  -e AGDISTIS_BASE_URI=http://dbpedia.org \
  -e AGDISTIS_CONTEXT=True \
  -m 8G \
  --restart always\
  aksw/agdistis:latest