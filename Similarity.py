from Levenshtein import distance, jaro, jaro_winkler, ratio
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance
from difflib import SequenceMatcher
from distance import jaccard, sorensen
from similarity.metric_lcs import MetricLCS
from similarity.ngram import NGram
from sklearn.metrics import jaccard_similarity_score
from sklearn.metrics.pairwise import cosine_similarity
from math import log
# pip install python-Levenshtein
# pip install numpy
# pip install pyxDamerauLevenshtein
# pip install Distance
# pip install strsim
# pip install sklearn


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
    try:
        return 1 - (distance(a, b) / max(len(a), len(b)))
        # return jaro(a, b)
        # return jaro_winkler(a, b)
        # return ratio(a, b)
        # return 1 - normalized_damerau_levenshtein_distance(a, b)
        # return SequenceMatcher(None, a, b).ratio()  # VERY SLOW ! BE CAREFUL !
        # return 1 - jaccard(a, b)
        # return 1 - sorensen(a, b)
        # return 1 - MetricLCS().distance(a, b)
        # return 1 - NGram(2).distance(a, b)
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
    bedroom_score = weight['bedroom'] * different_character(a['bedroom'], b['bedroom'])
    bathroom_score = weight['bathroom'] * different_character(a['bathroom'], b['bathroom'])
    return price_score + size_score + tower_score + floor_score + bedroom_score + bathroom_score


def detail_similarity(a, b):
    # intersect = sum([min(a[i], b[i]) for i in range(len(a))])
    # union = sum([max(a[i], b[i]) for i in range(len(a))])
    # return (1+intersect)/(1+union)
    # return jaccard_similarity_score(a, b)  # original jaccard
    return cosine_similarity([a], [b])[0][0]


def score_calculate(a, b, weight, half_weight_frequency):
    field_score = field_similarity(a, b, weight)
    detail_score = detail_similarity(a['detail'], b['detail'])
    length_weight = 1 / (1 + log(1 + (a['detail_length'] + b['detail_length']) / 2, half_weight_frequency + 1))
    return (length_weight * field_score) + ((1 - length_weight) * detail_score)
