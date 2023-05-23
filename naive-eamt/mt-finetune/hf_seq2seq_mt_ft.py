from datasets import load_dataset
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from transformers import DataCollatorForSeq2Seq
import numpy as np
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
import evaluate
"""
Script to fine-tune MT models
Ref: https://huggingface.co/docs/transformers/tasks/translation

To use: python hf_seq2seq_mt_ft.py
"""
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer_name = "facebook/mbart-large-50-many-to-many-mmt"

dataset_file = "data/json/fr_en_placeholder.json"
#output_dir = "ft_models/mbart50_mintaka_plc_pt_en_1"
output_dir = "ft_models/mbart50_mintaka_plc_fr_en_2"
#output_dir = "ft_models/mbart50_mintaka_plc_es_en_3"
#output_dir = "ft_models/mbart50_mintaka_plc_de_en_4"
#local_model = False
local_model = True
local_model_path = 'ft_models/mbart50_mintaka_plc_pt_en_1'
# Source and target language, usage and encoding depends upon the model tokenizer
src_lang = "fr_XX"
tgt_lang = "en_XX"

BATCH_SIZE = 32

prev_checkpoint = None
# prev_checkpoint = "ft_models/mbart50_mintaka_plc_de_en/checkpoint-6000"

if local_model:
    # load tokenizer
    tokenizer = MBart50TokenizerFast.from_pretrained(local_model_path, local_files_only=True, src_lang=src_lang, tgt_lang=tgt_lang)
    # load model
    model = MBartForConditionalGeneration.from_pretrained(local_model_path, local_files_only=True)
else:
    # load model tokenizer
    # Note: The model tokenizer always needs to know the language because it uses the language to add special tokens
    tokenizer = MBart50TokenizerFast.from_pretrained(tokenizer_name, src_lang=src_lang, tgt_lang=tgt_lang)
    # load model
    model = MBartForConditionalGeneration.from_pretrained(model_name)
    # special_tokens_dict
    extra_tokens_dict = []
    for i in range(7):
        extra_tokens_dict.append('[00%d]' % (i+1))
    # Modify tokenizer
    num_added_toks = tokenizer.add_tokens(extra_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))
    print("We have added", num_added_toks, "tokens:", extra_tokens_dict)
# load dataset
dataset = load_dataset("json", data_files=dataset_file)
#print(dataset)
# splitting dataset
dataset = dataset["train"].train_test_split(test_size=0.2, seed=42)
#print(dataset)
# Setup tokenization
# source_lang = "de"
# target_lang = "en"
# prefix if any
prefix = ""


def preprocess_function(examples):
    #print('Printing examples: %s' % examples)
    inputs = [prefix + example for example in examples['input']]
    targets = [example for example in examples['output']]
    model_inputs = tokenizer(inputs, text_target=targets, max_length=200, truncation=True, padding=True, return_tensors="pt")
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
    save_total_limit=3,
    num_train_epochs=10,
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
if prev_checkpoint:
    trainer.train(prev_checkpoint)
else:
    trainer.train()
trainer.save_model()