#!/bin/bash
# This script is to setup the different modules that need to intitialized.
# Execute this script while mentioning the modules that need to be downloaded and installed
# The syntax is ".\setup_data.sh {Included_module_01} {Included_module_02}
# In case no modules are passed, all the modules will be installed
# The tags for the modules are MAG: Mag Module, LIBRE: Libre module, OPUSMT: Helsinki-OPT Module, MGENRE: Genre Module
# Sample usage: In case only Libre and Genre Module need to be installed, following would be the execution command: 
# .\setup_data.sh LIBRE MGENRE
set -eu
# This might take some hours. Around 150 GB of storage space will be needed.
cd "${BASH_SOURCE%/*}"||echo "$(pwd)"
CUR_NEAMT=$(pwd)

# Download and unzip files
download_unzip_files() {
  readarray -d / -t FILE <<< "$1"
  #readarray -d . -t file_name <<< "${file_name[-1]}"
  #file_ext="${file_name[-1]}"
  #read -a file_ext <<< "${file_name[-1]}"
  file_name="${FILE[-1]%%.*}"
  file_ext="${FILE[-1]#*.}"
  file_ext="${file_ext%$'\n'}"
  if [[ "$4" = "no" ]] 
  then
    file_name="$2/$file_name"
  else
    file_name="$4"
  fi
  if [[ ! -d "$file_name" ]] && [[ -f "$file_name.$file_ext" ]]
  then
    echo "$file_name.$file_ext is present"
    if [[ "$file_ext" = "zip" ]] && [[ "$3" = "unzip" ]] 
    then
      unzip "$file_name.zip" -d "$2"
      rm "$file_name.zip"
      if [[ ! "$4" = "no" ]]
      then
        mv data/mag_data/index_bycontext "$file_name"
      fi
    fi
  elif [[ ! -f "$file_name.$file_ext" ]] && [[ ! -d "$file_name" ]]
  then
    echo "$file_name.$file_ext is not present"
    echo " "
    wget -O "$file_name.$file_ext" "$1"
    #echo "Unzipping"
    if [[ "$file_ext" = "zip" ]] && [[ "$3" = "unzip" ]]
    then
      unzip "$file_name.zip" -d "$2"
      rm "$file_name.zip"
      if [[ "$4" != "no" ]]
      then
        mv data/mag_data/index_bycontext "$file_name"
      fi
    fi
  else
    echo "$file_name.$file_ext is already unzipped"
  fi
}


# download all the relevant data


# -----------------MAG-----------------
# download mag data
MAG() {
  if [[ ! -d data/mag_data ]]
  then
    mkdir -p data/mag_data 
  fi

  echo 'MAG: Downloading Indexes for en, de, fr & es..'

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/en/indexdbpedia_en_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/en/index_bycontext.zip" "data/mag_data" "unzip" "data/mag_data/index_bycontext_en"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/de/index_bycontext.zip" "data/mag_data" "unzip" "data/mag_data/index_bycontext_de"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/it/indexdbpedia_it_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/ja/indexdbpedia_ja_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "https://files.dice-research.org/projects/AGDISTIS/dbpedia_index_2016-04/nl/indexdbpedia_nl_2016.zip" "data/mag_data" "unzip" "no"

  echo 'MAG: Indexes download finished.'
}

# download fasttext language classification model
if [[ ! -d data ]]
  then
    mkdir -p data 
  fi
download_unzip_files "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz" "data" "no_unzip" "no"


# -----------------LIBRE-----------------
# download libre repo

LIBRE() {
  if [[ ! -d data ]]
  then
    mkdir -p data 
  fi
  cd data
  if [[ ! -d LibreTranslate ]]
  then
    git clone --depth 1 https://github.com/LibreTranslate/LibreTranslate 
    
  fi

  # As described here: https://github.com/LibreTranslate/LibreTranslate/blob/main/CONTRIBUTING.md#build-with-docker
  cd LibreTranslate
  docker build -f docker/Dockerfile --build-arg with_models=true -t libretranslate .
  cd ../..
}

# -----------------OPUSMT-----------------
# Download Helsinki-OPT data

OPUSMT() {
  if [[ ! -d data ]]
  then
    mkdir -p data 
  fi
  cd data
  if [[ ! -d Opus-MT ]]
  then
    # git clone --depth 1 https://github.com/Helsinki-NLP/Opus-MT.git
    git clone --depth 1  https://github.com/dice-group/Opus-MT
  fi
  cd Opus-MT

  # Copy customized services.json
  mv services.json services.json.old
  cp $CUR_NEAMT/helsinki_opusmt_services.json ./services.json


  # Download and extract models
  mkdir -p models
  cd models

  # Lang codes: https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
  # Models: https://github.com/Helsinki-NLP/Opus-MT-train/tree/master/models

  declare -A model_urls=(
    ["de-en"]="https://object.pouta.csc.fi/OPUS-MT-models/de-en/opus-2020-02-26.zip" # sentencepiece
    ["es-en"]="https://object.pouta.csc.fi/OPUS-MT-models/es-en/opus-2019-12-04.zip" # BPE
    ["fr-en"]="https://object.pouta.csc.fi/OPUS-MT-models/fr-en/opus-2020-02-26.zip" # SentencePiece
    ["ru-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ru-en/opus-2020-02-26.zip" # SentencePiece
    ["nl-en"]="https://object.pouta.csc.fi/OPUS-MT-models/nl-en/opus-2019-12-05.zip" # SentencePiece
    # Not supported # ["zh-en"]="https://object.pouta.csc.fi/Tatoeba-MT-models/zho-eng/opus-2020-07-14.zip" # SentencePiece
    ["it-en"]="https://object.pouta.csc.fi/OPUS-MT-models/it-en/opus-2019-12-05.zip" # BPE
    ["pt-en"]="https://object.pouta.csc.fi/OPUS-MT-models/pt-en/opus-2019-12-05.zip" # BPE
    ["ja-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ja-en/opus-2019-12-05.zip" # BPE
    ["lt-en"]="https://object.pouta.csc.fi/OPUS-MT-models/lt-en/opus-2019-12-05.zip" # BPE
    ["id-en"]="https://object.pouta.csc.fi/OPUS-MT-models/id-en/opus-2019-12-05.zip" # BPE
    ["bn-en"]="https://object.pouta.csc.fi/OPUS-MT-models/bn-en/opus-2019-12-04.zip" # BPE
    ["et-en"]="https://object.pouta.csc.fi/OPUS-MT-models/et-en/opus-2019-12-04.zip" # BPE
    ["he-en"]="https://object.pouta.csc.fi/OPUS-MT-models/he-en/opus-2019-12-05.zip" # BPE
    # Doesn't work #["lv-en"]="https://object.pouta.csc.fi/OPUS-MT-models/lv-en/opus-2019-12-18.zip" # SentencePiece
    ["ro-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ro-en/opus-2019-12-05.zip" # BPE
    ["th-en"]="https://object.pouta.csc.fi/OPUS-MT-models/th-en/opus-2019-12-05.zip" # BPE
    ["uk-en"]="https://object.pouta.csc.fi/OPUS-MT-models/uk-en/opus-2019-12-05.zip" # BPE
    ["cs-en"]="https://object.pouta.csc.fi/OPUS-MT-models/cs-en/opus-2019-12-04.zip" # BPE
    ["fi-en"]="https://object.pouta.csc.fi/OPUS-MT-models/fi-en/opus-2019-12-04.zip" # BPE
    ["hi-en"]="https://object.pouta.csc.fi/OPUS-MT-models/hi-en/opus-2019-12-05.zip" # BPE
    ["ko-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ko-en/opus-2019-12-05.zip" # BPE
    ["pl-en"]="https://object.pouta.csc.fi/OPUS-MT-models/pl-en/opus-2019-12-05.zip" # BPE
    # Doesn't work #["sv-en"]="https://object.pouta.csc.fi/OPUS-MT-models/sv-en/opus-2020-02-26.zip" # SentencePiece
    ["tr-en"]="https://object.pouta.csc.fi/OPUS-MT-models/tr-en/opus-2019-12-05.zip" # BPE
    ["bg-en"]="https://object.pouta.csc.fi/OPUS-MT-models/bg-en/opus-2019-12-04.zip" # BPE
    ["ga-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ga-en/opus-2019-12-05.zip" # BPE
    ["ml-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ml-en/opus-2019-12-05.zip" # BPE
    # Doesn't work #["mr-en"]="https://object.pouta.csc.fi/OPUS-MT-models/mr-en/opus+bt-2020-05-23.zip" # BPE
    ["mk-en"]="https://object.pouta.csc.fi/OPUS-MT-models/mk-en/opus-2019-12-05.zip" # BPE
    ["nb-en"]="https://object.pouta.csc.fi/OPUS-MT-models/nb-en/opus-2019-12-05.zip" # BPE
    ["ne-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ne-en/opus-2019-12-05.zip" # BPE
    ["si-en"]="https://object.pouta.csc.fi/OPUS-MT-models/si-en/opus-2019-12-05.zip" # BPE
    ["te-en"]="https://object.pouta.csc.fi/OPUS-MT-models/te-en/opus-2019-12-05.zip" # BPE
    ["xh-en"]="https://object.pouta.csc.fi/OPUS-MT-models/xh-en/opus-2019-12-05.zip" # BPE
  )


  # Exclude models passed as command line arguments
  excluded_models=()
  for excluded_model in "$@"; do
    excluded_models+=("$excluded_model")
  done

  # Download and extract the models (excluding the ones passed as arguments)
  for lang_pair in "${!model_urls[@]}"; do
    if [[ " ${excluded_models[@]} " =~ " ${lang_pair} " ]]; then
      echo "Skipping download for $lang_pair"
      continue
    fi
    if [[ ! -d "$lang_pair" ]]
    then
      mkdir -p "$lang_pair"  
      model_url="${model_urls[$lang_pair]}"
      model_zip="${model_url##*/}"
      download_unzip_files "$model_url" "$lang_pair" "unzip" "no"
    fi 
   
  done


  cd ..

  # Build Docker image

  docker build . -t opus-mt

  cd ../..
}

# -----------------MGENRE-----------------
# download genre data
# Downloading models

MGENRE() {
  if [[ ! -d data/mgenre_data ]]
  then
    mkdir -p data/mgenre_data
  fi

  # untar
  if [[ -f data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz ]]
  then
    tar -xvf "data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz" -C data/mgenre_data
    rm data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz
  elif [[ ! -d data/mgenre_data/fairseq_multilingual_entity_disambiguation ]]
  then
    download_unzip_files "https://dl.fbaipublicfiles.com/GENRE/fairseq_multilingual_entity_disambiguation.tar.gz" "data/mgenre_data" "no_unzip" "no"
    tar -xvf "data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz" -C data/mgenre_data
    rm data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz
  else
    echo "data/mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz has been extracted"
  fi
  download_unzip_files "http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_trie_with_redirect.pkl" "data/mgenre_data" "no_unzip" "no"
  download_unzip_files "https://dl.fbaipublicfiles.com/GENRE/lang_title2wikidataID-normalized_with_redirect.pkl" "data/mgenre_data" "no_unzip" "no"
  download_unzip_files "http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_marisa_trie_with_redirect.pkl" "data/mgenre_data" "no_unzip" "no"
  
}


modules_included=0
for included_module in "$@"; do
  if [[ "$included_module" = "MAG" ]]
  then
    MAG
    ((modules_included++))
  elif [[ "$included_module" = "LIBRE" ]]
  then
    LIBRE
    ((modules_included++))
  elif [[ "$included_module" = "OPUSMT" ]]
  then
    OPUSMT
    ((modules_included++))
  elif [[ "$included_module" = "MGENRE" ]]
  then
    MGENRE
    ((modules_included++))
  fi
done

if [[ "$modules_included" = 0 ]]
then
  MAG
  LIBRE
  OPUSMT
  MGENRE
fi


# Download evaluation data
#cd ../../eval
#mkdir qald10 && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_10/main/data/qald_10/qald_10.json
#cd ..
#mkdir qald9plus && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_test_dbpedia.json
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_train_dbpedia.json
echo "Downloads finished!"
