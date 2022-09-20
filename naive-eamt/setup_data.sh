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
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/it/indexdbpedia_it_2016.zip
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/ja/indexdbpedia_ja_2016.zip
wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/nl/indexdbpedia_nl_2016.zip
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
# Download Helsinki-OPT data
git clone https://github.com/Helsinki-NLP/Opus-MT.git
cd Opus-MT
# Copy customized services.json
mv services.json services.json.old
cp ../../helsinki_opusmt_services.json ./services.json
mkdir models && cd "$_"
# Download models
mkdir de-en && cd "$_"
wget https://object.pouta.csc.fi/OPUS-MT-models/de-en/opus-2020-02-26.zip
unzip 'opus-2020-02-26.zip'
rm -rf 'opus-2020-02-26.zip'
cd ..
mkdir es-en && cd "$_"
wget https://object.pouta.csc.fi/OPUS-MT-models/es-en/opus-2019-12-04.zip
unzip 'opus-2019-12-04.zip'
rm -rf 'opus-2019-12-04.zip'
cd ..
mkdir fr-en && cd "$_"
wget https://object.pouta.csc.fi/OPUS-MT-models/fr-en/opus-2020-02-26.zip
unzip 'opus-2020-02-26.zip'
rm -rf 'opus-2020-02-26.zip'
cd ..
mkdir ru-en && cd "$_"
wget https://object.pouta.csc.fi/OPUS-MT-models/ru-en/opus-2020-02-26.zip
unzip 'opus-2020-02-26.zip'
rm -rf 'opus-2020-02-26.zip'
cd ..
mkdir nl-en && cd "$_"
wget https://object.pouta.csc.fi/OPUS-MT-models/nl-en/opus-2019-12-05.zip
unzip 'opus-2019-12-05.zip'
rm -rf 'opus-2019-12-05.zip'
cd ..
mkdir zh-en && cd "$_"
wget https://object.pouta.csc.fi/Tatoeba-MT-models/zho-eng/opus-2020-07-14.zip
unzip 'opus-2020-07-14.zip'
rm -rf 'opus-2020-07-14.zip'
cd ..
docker build . -t opus-mt
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
# Download evaluation data
cd ../../eval
mkdir qald10 && cd "$_"
wget https://raw.githubusercontent.com/KGQA/QALD_10/main/data/qald_10/qald_10.json
cd ..
mkdir qald9plus && cd "$_"
wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_test_dbpedia.json
echo "Downloads finished!"