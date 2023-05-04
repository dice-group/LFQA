#!/bin/bash
# create directories
mkdir -p dataset/mintaka
# Download mintaka
wget https://raw.githubusercontent.com/amazon-science/mintaka/main/data/mintaka_test.json -P dataset/mintaka/
wget https://raw.githubusercontent.com/amazon-science/mintaka/main/data/mintaka_train.json -P dataset/mintaka/
wget https://raw.githubusercontent.com/amazon-science/mintaka/main/data/mintaka_dev.json -P dataset/mintaka/
