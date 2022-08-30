#!/bin/bash
# This might take some hours. Around 150 GB of storage space will be needed.
cd "${BASH_SOURCE%/*}" || exit
# download all the relevant data
# download mag data
mkdir -p data/mag_data && cd "$_"
echo 'MAG: Downloading Indexes for en, de, fr & es..'
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/indexdbpedia_en_2016.zip
wget -O index_bycontext_en.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip

wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip
wget -O index_bycontext_de.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip

wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip
echo 'MAG: Indexes download finished.'
echo 'MAG: Unzipping files..'
# Unzip the files
unzip index_bycontext_en.zip
mv index_bycontext index_bycontext_en
unzip index_bycontext_de.zip
mv index_bycontext index_bycontext_de
rm -rf index_bycontext_en.zip index_bycontext_de.zip
unzip '*.zip'
rm -rf *.zip
echo 'MAG: Pulling Docker Image'
docker pull aksw/agdistis
echo 'MAG: Finished!'
cd ..
# download fasttext language classification model
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
# download libre repo
git clone https://github.com/LibreTranslate/LibreTranslate
cd LibreTranslate
docker build --build-arg with_models=true -t libretranslate .
cd ..
# download genre data
# Downloading models
mkdir mgenre_data && cd "$_"
wget https://dl.fbaipublicfiles.com/GENRE/fairseq_multilingual_entity_disambiguation.tar.gz
# untar
tar -xvf fairseq_multilingual_entity_disambiguation.tar.gz
wget http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_trie_with_redirect.pkl
wget https://dl.fbaipublicfiles.com/GENRE/lang_title2wikidataID-normalized_with_redirect.pkl
wget http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_marisa_trie_with_redirect.pkl
echo "Downloads finished!"