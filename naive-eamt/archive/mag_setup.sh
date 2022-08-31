#!/bin/bash
mkdir mag_data && cd "$_"
echo 'MAG Setup: Downloading Indexes for en, de, fr & es..'
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/indexdbpedia_en_2016.zip
wget -O index_bycontext_en.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip

wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip
wget -O index_bycontext_de.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip

wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip
echo 'MAG Setup: Indexes download finished.'
echo 'MAG Setup: Pulling Docker Image'
docker pull aksw/agdistis
echo 'MAG Setup: Finished!'