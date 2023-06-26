#!/bin/bash
set -eu
# This might take some hours. Around 150 GB of storage space will be needed.
cd "${BASH_SOURCE%/*}"||echo "$(pwd)"

# download all the relevant data
# download mag data
if [[ ! -d data/mag_data ]]
then
  mkdir -p data/mag_data 
fi

#cd data/mag_data

#echo "$(pwd)"
echo 'MAG: Downloading Indexes for en, de, fr & es..'
download_files() {
  readarray -d / -t file_name <<< "$1"
  readarray -d . -t file_name <<< "${file_name[-1]}"
  #file_ext="${file_name[-1]}"
  read -a file_ext <<< "${file_name[-1]}"
  #echo "$file_name.$file_ext"
  file_name="$2/$file_name"
  #echo "$file_name"
  if [[ ! -d "$file_name" ]] && [[ -f "$file_name.$file_ext" ]]
  then
    echo "$file_name.$file_ext is present"
    #echo "Unzipping"
    #echo "$file_name"
    if [[ "$file_ext" = "zip" ]]
    then
      unzip "$file_name.zip" -d "$2"
      rm "$file_name.zip"
    fi
  elif [[ ! -f "$file_name.$file_ext" ]] && [[ ! -d "$file_name" ]]
  then
    echo "$file_name.$file_ext is not present"
    #echo "$file_ext"
    wget -O "$file_name.$file_ext" "$1"
    #echo "Unzipping"
    if [[ "$file_ext" = "zip" ]]
    then
      unzip "$file_name.zip" -d "$2"
      rm "$file_name.zip"
    fi
  else
    echo "$file_name.$file_ext is already unzipped"
  fi
}

download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/indexdbpedia_en_2016.zip" "data/mag_data"

file_name=data/mag_data/index_bycontext
echo "$file_name"
if [[ ! -d "$file_name"_en ]] && [[ -f "$file_name.zip" ]]
then
  echo "$file_name.zip is present"
  echo "Unzipping"
  unzip "$file_name".zip -d data/mag_data
  mv data/mag_data/index_bycontext data/mag_data/index_bycontext_en
  rm "$file_name.zip"
elif [[ ! -f "$file_name.zip" ]] && [[ ! -d "$file_name"_en ]]
then
  echo "$file_name.zip is not present"
  wget -O "$file_name".zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip
  echo "Unzipping"
  unzip "$file_name.zip" -d data/mag_data
  mv data/mag_data/index_bycontext data/mag_data/index_bycontext_en
  rm "$file_name.zip"
else
  echo "$file_name.zip is already unzipped"
fi

#download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip" "data/mag_data"
#wget -O index_bycontext_en.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/en/index_bycontext.zip
#unzip index_bycontext.zip
#mv index_bycontext index_bycontext_en


download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/indexdbpedia_de_2016.zip


file_name=data/mag_data/index_bycontext
#echo "$file_name"
if [[ ! -d "$file_name"_de ]] && [[ -f "$file_name.zip" ]]
then
  echo "$file_name.zip is present"
  echo "Unzipping"
  unzip "$file_name.zip" -d data/mag_data
  mv data/mag_data/index_bycontext data/mag_data/index_bycontext_de
  rm "$file_name.zip"
elif [[ ! -f "$file_name.zip" ]] && [[ ! -d "$file_name"_de ]]
then
  echo "$file_name.zip is not present"
  wget -O "$file_name".zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip
  echo "Unzipping"
  unzip "$file_name.zip" -d data/mag_data
  mv data/mag_data/index_bycontext data/mag_data/index_bycontext_de
  rm "$file_name.zip"
else
  echo "$file_name.zip is already unzipped"
fi

#download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip" "data/mag_data"
#wget -O index_bycontext_de.zip http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/de/index_bycontext.zip
#unzip index_bycontext.zip
#mv index_bycontext index_bycontext_de


download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/fr/indexdbpedia_fr_2016.zip
download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/es/indexdbpedia_es_2016.zip
download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/it/indexdbpedia_it_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/it/indexdbpedia_it_2016.zip
download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/ja/indexdbpedia_ja_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/ja/indexdbpedia_ja_2016.zip
download_files "http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/nl/indexdbpedia_nl_2016.zip" "data/mag_data"
#wget http://hobbitdata.informatik.uni-leipzig.de/agdistis/dbpedia_index_2016-04/nl/indexdbpedia_nl_2016.zip
echo 'MAG: Indexes download finished.'
echo 'MAG: Unzipping files..'
# Unzip the files

#rm -rf index_bycontext.zip
#rm -rf index_bycontext_en.zip index_bycontext_de.zip
#cd data/mag_data
#unzip '*.zip'  
#rm -rf *.zip
echo 'MAG: Finished!'
#cd ..
#cd ..

# download fasttext language classification model
nonzip() {
  readarray -d / -t file_name <<< "$1"
  #readarray -d . -t file_name <<< "${file_name[-1]}"
  #file_ext="${file_name[-1]}"
  read -a file_name <<< "${file_name[-1]}"
  #echo "$file_name.$file_ext"
  file_name="$2/$file_name"
  #echo "$file_name"
  if [[ ! -f "$file_name" ]]
  then
    echo "$file_name is not present"
    wget -O "$file_name" "$1"
  else
    echo "$file_name is present"
  fi
}
nonzip "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz" "data"
#wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz
# download libre repo
cd data
if [[ ! -d LibreTranslate ]]
then
  git clone --depth 1 https://github.com/LibreTranslate/LibreTranslate 
  cd LibreTranslate
  docker build -f docker/Dockerfile --build-arg with_models=true -t libretranslate .
  cd ..
fi
#git clone --depth 1 https://github.com/LibreTranslate/LibreTranslate
#cd LibreTranslate
#docker build -f docker/Dockerfile --build-arg with_models=true -t libretranslate .
#cd ..
# Download Helsinki-OPT data
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
    mkdir -p "$lang_pair" && cd "$lang_pair" 
    model_url="${model_urls[$lang_pair]}"
    model_zip="${model_url##*/}"
    wget "$model_url"
    unzip -n "$model_zip"
    rm -f "$model_zip"
    cd ..
  fi 
 
done


cd ..

# Build Docker image


#(Check if group exists)
#groupadd docker
#usermod -aG docker "${USER}"

#su -s (logout and log back in)
#docker build . -t opus-mt


#cd ../..
#docker build . -t opus-mt
cd ..
# download genre data
# Downloading models
#echo "$(pwd)"
if [[ ! -d mgenre_data ]]
then
  mkdir -p mgenre_data 
fi


# untar
if [[ -f mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz ]]
then
  tar -xvf "mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz" -C mgenre_data
  rm mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz
elif [[ ! -d mgenre_data/fairseq_multilingual_entity_disambiguation ]]
then
  nonzip "https://dl.fbaipublicfiles.com/GENRE/fairseq_multilingual_entity_disambiguation.tar.gz" "mgenre_data"
  tar -xvf "mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz" -C mgenre_data
  rm mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz
else
  echo "mgenre_data/fairseq_multilingual_entity_disambiguation.tar.gz has been extracted"
fi
nonzip "http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_trie_with_redirect.pkl" "mgenre_data"
nonzip "https://dl.fbaipublicfiles.com/GENRE/lang_title2wikidataID-normalized_with_redirect.pkl" "mgenre_data"
nonzip "http://dl.fbaipublicfiles.com/GENRE/titles_lang_all105_marisa_trie_with_redirect.pkl" "mgenre_data"
# Download evaluation data
#cd ../../eval
#mkdir qald10 && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_10/main/data/qald_10/qald_10.json
#cd ..
#mkdir qald9plus && cd "$_"
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_test_dbpedia.json
#wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_train_dbpedia.json
echo "Downloads finished!"


