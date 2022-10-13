from evaluate import load

bertscore = load("bertscore")
bleurt = load("bleurt", module_type="metric", checkpoint="bleurt-large-128")


# Execute sample computation to initialize the model
predictions = ["hi there", "mister kenobi"]
references = ["hello there", "general kenobi"]

bertscore_results = bertscore.compute(predictions=predictions, references=references, lang="en")
bleurt_results = bleurt.compute(predictions=predictions, references=references)