# pip install pythainlp
from pythainlp.tokenize import word_tokenize
# from pythainlp.ner import thainer
from Levenshtein import distance # pip install python-Levenshtein
from math import log
from operator import itemgetter
from collections import Counter
from time import time


def different_numerical(a, b):
    if a is b:
        return 1
    if a is None or b is None:
        return 0
    return 1 - (abs(a - b) * 2 / (a + b))


def different_character(a, b):
    # pip install python-Levenshtein
    return 1 - (distance(a, b) / max(len(a), len(b)))


def field_similarity(a, b, weight):
    price_score = weight['price'] * different_numerical(a['price'][0], b['price'][0])
    size_score = weight['size'] * different_numerical(a['size'], b['size'])
    tower_score = weight['tower'] * different_character(a['tower'], b['tower'])
    floor_score = weight['floor'] * different_character(a['floor'], b['floor'])
    type_score = weight['type'] * different_character(a['type'], b['type'])
    return price_score + size_score + tower_score + floor_score + type_score


def detail_similarity(a, b):
    size_a = sum(a.values())
    size_b = sum(b.values())
    intersect = sum([min(a[word], b[word]) for word in set(a.keys()).intersection(set(b.keys()))])
    return (1+intersect)/(1+min(size_a, size_b))


def score_calculate(docs, parameter):
    tokenize_time = 0
    calculate_time = 0
    duplicate = {}
    calculated_docs = []
    score = []
    for doc in docs:
        is_duplicate = False
        doc['detail_length'] = len(doc['detail'])
        a = time()
        word_list = word_tokenize(doc['detail'], engine='newmm')
        b = time()
        word_list = {k: v for k, v in Counter(word_list).items() if not (k.isspace() or k.replace('.','',1).isdecimal())}
        doc['detail'] = dict(Counter(word_list).most_common(parameter['most_frequency_word']))
        tokenize_time += b - a
        for calculated_doc in calculated_docs:
            field_score = field_similarity(doc, calculated_doc, parameter['weight'])
            detail_score = detail_similarity(doc['detail'], calculated_doc['detail'])
            length_weight = 1 / (1 + log(1 + (doc['detail_length'] + calculated_doc['detail_length']) / 2, 10))
            confidence = (length_weight * field_score) + ((1 - length_weight) * detail_score)
            if confidence >= parameter['hard_threshold']:
                if calculated_doc['id'] in duplicate:
                    duplicate[calculated_doc['id']].append(doc['id'])
                else:
                    duplicate[calculated_doc['id']] = [calculated_doc['id'], doc['id']]
                is_duplicate = True
                break
            if confidence >= parameter['min_confidence']:
                score.append([doc['id'], calculated_doc['id'], confidence])
        if not is_duplicate:
            calculated_docs.append(doc)
        calculate_time += time() - b
    score = sorted(score, key=itemgetter(2), reverse=True)
    medium_score = [s for s in score if s[2] >= parameter['soft_threshold']]
    weak_score = [s for s in score if s[2] < parameter['soft_threshold']]
    return duplicate, medium_score, weak_score, tokenize_time, calculate_time
