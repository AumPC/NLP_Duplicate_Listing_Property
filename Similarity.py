from Levenshtein import distance
from math import log


def sampling(text, rate):
    width = rate*len(text)/10
    return ' '.join([text[int(len(text)/i-width):int(len(text)/i+width)] for i in range(1, 10, 2)])


def different_numerical(a, b):
    try:
        return 1 - (abs(a - b) * 2 / (a + b))
    except TypeError:
        return int(a is b)
    except ZeroDivisionError:
        return 1


def different_character(a, b):
    # pip install python-Levenshtein
    try:
        return 1 - (distance(a, b) / max(len(a), len(b)))
    except TypeError:
        return int(a is b)
    except ZeroDivisionError:
        return 1


def field_similarity(a, b, weight):
    try:
        price_score = weight['price'] * different_numerical(a['price'][0], b['price'][0])
    except TypeError:
        price_score = weight['price'] * int(a['price'] is b['price'])
    size_score = weight['size'] * different_numerical(a['size'], b['size'])
    tower_score = weight['tower'] * different_character(a['tower'], b['tower'])
    floor_score = weight['floor'] * different_character(a['floor'], b['floor'])
    type_score = weight['type'] * different_character(a['type'], b['type'])
    return price_score + size_score + tower_score + floor_score + type_score


def detail_similarity(a, b):
    intersect = sum([min(a[word], b[word]) for word in set(a.keys()).intersection(set(b.keys()))])
    union = sum([max(a.get(word,0), b.get(word,0)) for word in set(a.keys()).union(set(b.keys()))])
    return (1+intersect)/(1+union)


def score_calculate(a, b, weight, half_weight_frequency):
    field_score = field_similarity(a, b, weight)
    detail_score = detail_similarity(a['detail'], b['detail'])
    length_weight = 1 / (1 + log(1 + (a['detail_length'] + b['detail_length']) / 2, half_weight_frequency + 1))
    return (length_weight * field_score) + ((1 - length_weight) * detail_score)
