#!/bin/bash
read -p "Are you sure you want to continue? <y/N> " prompt
if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]
then
  echo 'Deleting all evaluation files...'
  rm -rf pred_results*
  rm -rf *_gold_file.txt
  rm -rf translated_qald
  rm -rf experiment_details.tsv
  rm -rf evaluation_results.tsv
  rm -rf *_logs.txt
  echo 'Done!'
else
  exit 0
fi