#!/bin/bash
echo 'Starting requirements installation'
# PyTorch CPU installation
conda install pytorch torchvision torchaudio cpuonly -c pytorch
# Installing Fairseq (because of breaking changes it is installed from particular branch)
git clone --branch fixing_prefix_allowed_tokens_fn https://github.com/nicola-decao/fairseq
cd fairseq
pip install --editable ./
cd ..
# Installing requirements from requirements.txt
pip install -r requirements.txt
# Setup mGenre
git clone https://github.com/facebookresearch/GENRE.git
cd GENRE
python setup.py build
python setup.py install
cd ..
# Downloading models
mkdir mgenre_data && cd "$_"
wget https://dl.fbaipublicfiles.com/GENRE/fairseq_multilingual_entity_disambiguation.tar.gz
# untar
tar -xvf fairseq_multilingual_entity_disambiguation.tar.gz
wget http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_trie_with_redirect.pkl
wget https://dl.fbaipublicfiles.com/GENRE/lang_title2wikidataID-normalized_with_redirect.pkl
wget http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_marisa_trie_with_redirect.pkl
cd ..
# Downloading spacy's multilingual entity recognition model
python -m spacy download xx_ent_wiki_sm
# to allow notebooks to see this environment
conda install ipykernel -y
# rename if needed
ipython kernel install --user --name=lf_ner
# Mag Setup
bash mag_setup.sh
echo 'Done!'