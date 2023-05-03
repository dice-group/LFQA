#!/bin/bash
# create directories
mkdir -p dataset/qald10
mkdir -p dataset/qald9plus
# Download qald10
wget https://raw.githubusercontent.com/KGQA/QALD_10/main/data/qald_10/qald_10.json -P dataset/qald10/
# Download qald9
wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_test_dbpedia.json -P dataset/qald9plus/
wget https://raw.githubusercontent.com/KGQA/QALD_9_plus/main/data/qald_9_plus_train_dbpedia.json -P dataset/qald9plus/