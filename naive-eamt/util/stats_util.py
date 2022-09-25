import copy
# Initialize vars
stats = {
    'placeholder_count': {
        'total': 0,
        'translated': 0,
        'no_en_lbl_count': 0
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
