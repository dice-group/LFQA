import copy
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
