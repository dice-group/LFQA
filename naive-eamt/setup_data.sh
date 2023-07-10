#!/bin/bash
set -eu
# This might take some hours. Around 150 GB of storage space will be needed.
cd "${BASH_SOURCE%/*}"||echo "$(pwd)"

# Download and unzip files
download_unzip_files() {
  readarray -d / -t file_name <<< "$1"
  readarray -d . -t file_name <<< "${file_name[-1]}"
  #file_ext="${file_name[-1]}"
  read -a file_ext <<< "${file_name[-1]}"
  if [[ "$4" = "no" ]] 
  then
    file_name="$2/$file_name"
  else
    file_name="$4"
  fi
  if [[ "$file_ext" = "ftz" ]]
  then
    file_name="$file_name.176"
  elif [[ "$file_ext" = "gz" ]]
  then
    file_name="$file_name.tar"
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

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/indexdbpedia_en_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip" "data/mag_data" "unzip" "data/mag_data/index_bycontext_en"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip" "data/mag_data" "unzip" "data/mag_data/index_bycontext_de"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/it/indexdbpedia_it_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/ja/indexdbpedia_ja_2016.zip" "data/mag_data" "unzip" "no"

  download_unzip_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/nl/indexdbpedia_nl_2016.zip" "data/mag_data" "unzip" "no"

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
    git clone --depth 1 https://github.com/Helsinki-NLP/Opus-MT.git
  fi
  cd Opus-MT

  # Copy customized services.json
  mv services.json services.json.old
  cp ../../helsinki_opusmt_services.json ./services.json


  # Download and extract models
  mkdir -p models
  cd models

  declare -A model_urls=(
    ["de-en"]="https://object.pouta.csc.fi/OPUS-MT-models/de-en/opus-2020-02-26.zip"
    ["es-en"]="https://object.pouta.csc.fi/OPUS-MT-models/es-en/opus-2019-12-04.zip"
    ["fr-en"]="https://object.pouta.csc.fi/OPUS-MT-models/fr-en/opus-2020-02-26.zip"
    ["ru-en"]="https://object.pouta.csc.fi/OPUS-MT-models/ru-en/opus-2020-02-26.zip"
    ["nl-en"]="https://object.pouta.csc.fi/OPUS-MT-models/nl-en/opus-2019-12-05.zip"
    ["zh-en"]="https://object.pouta.csc.fi/Tatoeba-MT-models/zho-eng/opus-2020-07-14.zip"
    ["it-en"]="https://object.pouta.csc.fi/OPUS-MT-models/it-en/opus-2019-12-05.zip"
    ["pt-en"]="https://object.pouta.csc.fi/OPUS-MT-models/pt-en/opus-2019-12-05.zip"
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



for included_module in "$@"; do
  if [[ "$included_module" = "MAG" ]]
  then
    MAG
  elif [[ "$included_module" = "LIBRE" ]]
  then
    LIBRE
  elif [[ "$included_module" = "OPUSMT" ]]
  then
    OPUSMT
  elif [[ "$included_module" = "MGENRE" ]]
  then
    MGENRE
  fi
done


# Download evaluation data
#cd ../../eval
#mkdir qald10 && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_10/main/data/qald_10/qald_10.json
#cd ..
#mkdir qald9plus && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_test_dbpedia.json
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_train_dbpedia.json
echo "Downloads finished!"
