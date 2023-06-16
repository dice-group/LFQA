#!/bin/sh
set -eu
base=$1
globalargs="--redis-address localhost"
args="$globalargs --path $base/qald9plustest --dataset-format=qald_qae --dataset-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json"
./analysis.py --metric bleu4 $args
./analysis.py --metric sacrebleu $args
./analysis.py --metric entitiesfound $args
./analysis.py --metric labels $args
args="$globalargs --path $base/qald9plustrain --dataset-format=qald_qae --dataset-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json"
./analysis.py --metric bleu4 $args
./analysis.py --metric sacrebleu $args
./analysis.py --metric entitiesfound $args
./analysis.py --metric labels $args
args="$globalargs --path $base/qald10 --dataset-format=qald_qae --dataset-file $HOME/.local/share/datasets/qald-10-query-entities.json"
./analysis.py --metric bleu4 $args
./analysis.py --metric sacrebleu $args
./analysis.py --metric entitiesfound $args
./analysis.py --metric labels $args
args="$globalargs --path $base/mintaka --dataset-format=mintaka --dataset-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json"
./analysis.py --metric bleu4 $args
./analysis.py --metric sacrebleu $args
./analysis.py --metric entitiesfound $args
./analysis.py --metric labels $args
