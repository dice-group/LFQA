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

./average_analysis.py --path $base/qald9plustest --problematicity-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.classes --problematicity-threshold 0.0
./average_analysis.py --path $base/qald9plustest --problematicity-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.classes --problematicity-threshold 0.5
./average_analysis.py --path $base/qald9plustest --problematicity-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-test-query-entities.json.classes --problematicity-threshold 1.0
./average_analysis.py --path $base/qald9plustrain --problematicity-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.classes --problematicity-threshold 0.0
./average_analysis.py --path $base/qald9plustrain --problematicity-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.classes --problematicity-threshold 0.5
./average_analysis.py --path $base/qald9plustrain --problematicity-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.distinctlabels --classes-file $HOME/.local/share/datasets/qald-9-plus-train-query-entities.json.classes --problematicity-threshold 1.0
./average_analysis.py --path $base/qald10 --problematicity-file $HOME/.local/share/datasets/qald-10-query-entities.json.distinctlabels --problematicity-threshold 0.0 --classes-file $HOME/.local/share/datasets/qald-10-query-entities.json.classes
./average_analysis.py --path $base/qald10 --problematicity-file $HOME/.local/share/datasets/qald-10-query-entities.json.distinctlabels --problematicity-threshold 0.5 --classes-file $HOME/.local/share/datasets/qald-10-query-entities.json.classes
./average_analysis.py --path $base/qald10 --problematicity-file $HOME/.local/share/datasets/qald-10-query-entities.json.distinctlabels --problematicity-threshold 1.0 --classes-file $HOME/.local/share/datasets/qald-10-query-entities.json.classes
./average_analysis.py --path $base/mintaka --problematicity-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.distinctlabels --problematicity-threshold 0.0 --classes-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.classes
./average_analysis.py --path $base/mintaka --problematicity-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.distinctlabels --problematicity-threshold 0.5 --classes-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.classes
./average_analysis.py --path $base/mintaka --problematicity-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.distinctlabels --problematicity-threshold 1.0 --classes-file $HOME/.local/share/datasets/Mintaka/v1.1/mintaka_dev.json.classes
