import json


def is_equal(a, b):
    try:
        a = list(a.values())[0]
        b = list(b.values())[0]

        return a['type'] == b['type'] and a['value'] == b['value']
    except Exception as e:
        return False

def precision_recall_f1(relevant_items, retrieved_items, compare_func = None):
    """
    Precision (P) is the fraction of retrieved documents that are relevant
    Recall (R) is the fraction of relevant documents that are retrieved
    F1 is the harmonic mean of precision and recall

    Usage:
    precision, recall, f1 = precision_recall_f1(relevant_items, retrieved_items, compare_func)
    
    where relevant or retrieved items are: sparql_result['results']['bindings'] (if SPARQL results are used)
    """

    if not compare_func:
        def is_equal(a, b):
            return a == b
        compare_func = is_equal

    relevant_items_retrieved = 0

    for relevant in relevant_items:
        for retrieved in retrieved_items:
            if compare_func(relevant, retrieved):
                relevant_items_retrieved += 1
                break
    
    precision = relevant_items_retrieved/len(retrieved_items) if len(retrieved_items) > 0 else 0
    recall = relevant_items_retrieved/len(relevant_items) if len(relevant_items) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

def read_json(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except Exception as e:
        print(str(e))
        return None
    
def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def extract_string_qald(json_data, language):
    for question in json_data['question']:
        if question['language'] == language:
            return question['string']