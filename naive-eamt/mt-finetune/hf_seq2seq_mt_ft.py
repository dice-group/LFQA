from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers import DataCollatorForSeq2Seq
import numpy as np
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
import evaluate
import logging
import os
# Select GPUs to train (usually trains faster on a single GPU)
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
"""
Script to fine-tune MT models
Ref: https://huggingface.co/docs/transformers/tasks/translation

To use: python hf_seq2seq_mt_ft.py
"""
# Set this value according to your GPU
BATCH_SIZE = 32
TRAIN_EPOCHS = 30

def fine_tune_mt_model(model_name, tokenizer_name, dataset_files, output_dir, local_model, local_model_path, src_lang, tgt_lang):

    if local_model:
        # load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True, src_lang=src_lang, tgt_lang=tgt_lang)
        # load model
        model = AutoModelForSeq2SeqLM.from_pretrained(local_model_path, local_files_only=True)
    else:
        # load model tokenizer
        # Note: The model tokenizer always needs to know the language because it uses the language to add special tokens
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, src_lang=src_lang, tgt_lang=tgt_lang)
        # load model
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        # special_tokens_dict
        extra_tokens_dict = []
        for i in range(7):
            extra_tokens_dict.append('[00%d]' % (i+1))
        # Modify tokenizer
        num_added_toks = tokenizer.add_tokens(extra_tokens_dict)
        model.resize_token_embeddings(len(tokenizer))
        logging.info("We have added %d tokens: %s" % (num_added_toks, extra_tokens_dict))
    # print model info
    logging.info("Starting fine-tuning of '%s' with '%s', output will saved at '%s'" % (model.name_or_path, dataset_files, output_dir))
    # load dataset
    dataset = load_dataset("json", data_files=dataset_files)
    # shuffle dataset
    dataset = dataset.shuffle(seed=42)
    # splitting dataset
    dataset = dataset["train"].train_test_split(test_size=0.2, seed=42)
    # print dataset info
    logging.info("Dataset information: %s" % str(dataset))
    prefix = ""


    def preprocess_function(examples):
        #print('Printing examples: %s' % examples)
        inputs = [prefix + example for example in examples['input']]
        targets = [example for example in examples['output']]
        # setting max length to 512
        model_inputs = tokenizer(inputs, text_target=targets, max_length=512, truncation=True, padding=True, return_tensors="pt")
        return model_inputs


    # tokenize the inputs
    tokenized_inputs = dataset.map(preprocess_function, batched=True)

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    sacrebleu = evaluate.load("sacrebleu")


    # functions to compute SacreBleu score for the predictions
    def postprocess_text(preds, labels):
        preds = [pred.strip() for pred in preds]
        labels = [[label.strip()] for label in labels]

        return preds, labels


    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)

        result = sacrebleu.compute(predictions=decoded_preds, references=decoded_labels)
        result = {"bleu": result["score"]}

        prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
        result["gen_len"] = np.mean(prediction_lens)
        result = {k: round(v, 4) for k, v in result.items()}
        return result


    # Train setup

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="steps",
        eval_steps=500,
        learning_rate=2e-5,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        weight_decay=0.01,
        save_total_limit=1,
        num_train_epochs=TRAIN_EPOCHS,
        predict_with_generate=True,
        fp16=True,
        push_to_hub=False,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_inputs["train"],
        eval_dataset=tokenized_inputs["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model()