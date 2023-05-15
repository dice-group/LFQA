import copy
from threading import Lock

# Thread safe access
lock = Lock()
# Initialize vars
stats = {
    'placeholder_count': {
        'total': 0,
        'translated': 0
    },
    'english_label_count': {
        'total_found': 0,
        'not_found': 0,
        'trans_copied': 0
    },
    'query_count': 0
}

default_stats = copy.deepcopy(stats)


def reset_stats():
    global stats
    for item in stats:
        stats[item] = copy.deepcopy(default_stats[item])


def reset_placeholder_stats():
    global stats
    stats['placeholder_count'] = copy.deepcopy(default_stats['placeholder_count'])
    stats['english_label_count'] = copy.deepcopy(default_stats['english_label_count'])

def update_global_stats(cur_stats):
    global lock
    lock.acquire()
    global stats
    stats = add_nested_dictionaries(stats, cur_stats)
    lock.release()

def add_nested_dictionaries(dict1, dict2):
    result = {}

    for key in set(dict1.keys()).union(dict2.keys()):
        if key in dict1 and key in dict2:
            if isinstance(dict1[key], int) and isinstance(dict2[key], int):
                result[key] = dict1[key] + dict2[key]
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                result[key] = add_nested_dictionaries(dict1[key], dict2[key])
            else:
                result[key] = dict1[key] if key in dict1 else dict2[key]
        else:
            result[key] = dict1.get(key, dict2.get(key))

    return result