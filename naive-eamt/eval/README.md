## Evaluation
**Note**: At the moment, the implementation can only read the evaluation files in [QALD](https://qald.aksw.org/) format.

To evaluate the configured pipelines, the [eval_config.json](eval_config.json) file needs to be modified. Afterwards, perform the following steps:
- Execute ```python run_test.py``` to generate the gold and prediction files for all the pipelines;
- Execute ```python eval_test.py``` to evaluate each prediction file against its gold file using [BENG](https://beng.dice-research.org/gerbil/);
- Wait for BENG to finish evaluation;
- Execute ```python gen_eval_results.py``` to extract the results from BENG and write it to a tsv file named ```evaluation_results.tsv```;
- Optionally, execute ```python format_translated_qald.py``` to format the predictions back into QALD format.