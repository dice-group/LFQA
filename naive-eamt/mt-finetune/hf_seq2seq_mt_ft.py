from datasets import load_dataset
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from transformers import DataCollatorForSeq2Seq
import numpy as np
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
import evaluate
"""
Script to fine-tune MT models
Ref: https://huggingface.co/docs/transformers/tasks/translation
"""
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer_name = "facebook/mbart-large-50-many-to-many-mmt"
dataset_dir = "data/json/"
output_dir = "ft_models/mbart50_mintaka_plc"
# load model tokenizer
tokenizer = MBart50TokenizerFast.from_pretrained(tokenizer_name)
# load model
model = MBartForConditionalGeneration.from_pretrained(model_name)

# load dataset
dataset = load_dataset("json", data_dir="data/json/")
# splitting dataset
dataset = dataset["train"].train_test_split(test_size=0.2)

# Setup tokenization
# source_lang = "de"
# target_lang = "en"
# prefix if any
prefix = ""


def preprocess_function(examples):
    inputs = [prefix + example['input'] for example in examples]
    targets = [example['output'] for example in examples]
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
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=2,
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