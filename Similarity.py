# pip install pythainlp
from pythainlp.tokenize import word_tokenize
# from pythainlp.ner import thainer
from math import log
from operator import itemgetter
from collections import Counter
from time import time


def different_numerical(a, b):
    if a is None and b is None:
        return 1
    if a is None or b is None:
        return 0
    if a == 0 and b == 0:
        return 1
    return 1 - (abs(a - b) * 2 / (a + b))


def different_character(a, b):
    # Levenshtein distance
    metrix = []
    for i in range(len(a) + 1):
        m = []
        for j in range(len(b) + 1):
            m.append(0)
        metrix.append(m)
    for i in range(len(a) + 1):
        metrix[i][0] = i
    for i in range(len(b) + 1):
        metrix[0][i] = i
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i] == b[j]:
                metrix[i+1][j+1] = metrix[i][j]
            else:
                metrix[i+1][j+1] = min(metrix[i][j], metrix[i+1][j], metrix[i][j+1]) + 1
    return 1 - (metrix[len(a)][len(b)] / max(len(a), len(b)))


def field_similarity(a, b, weight):
    price_score = weight['price'] * different_numerical(a['price'][0], b['price'][0])
    size_score = weight['size'] * different_numerical(a['size'], b['size'])
    tower_score = weight['tower'] * different_character(a['tower'], b['tower'])
    floor_score = weight['floor'] * different_character(a['floor'], b['floor'])
    type_score = weight['type'] * different_character(a['type'], b['type'])
    return price_score + size_score + tower_score + floor_score + type_score


def detail_similarity(bag_A, bag_B):
    size_A = 0
    size_B = 0
    intersect = 0
    for word in bag_A:
        size_A += bag_A[word]
    for word in bag_B:
        size_B += bag_B[word]
        if word in bag_A:
            intersect += min(bag_A[word], bag_B[word])
    return (1+intersect)/(1+min(size_A, size_B))


def score_calculate(docs, parameter):
    weight = parameter['weight']
    min_confidence = parameter['min_confidence']
    hard_threshold = parameter['hard_threshold']
    soft_threshold = parameter['soft_threshold']
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
        doc['detail'] = {k: v for k, v in Counter(word_list).items() if not (k.isspace() or k.replace('.','',1).isdecimal())}
        tokenize_time += b - a
        for calculated_doc in calculated_docs:
            field_score = field_similarity(doc, calculated_doc, weight)
            detail_score = detail_similarity(doc['detail'], calculated_doc['detail'])
            length_weight = 1 / (1 + log(1 + (doc['detail_length'] + calculated_doc['detail_length']) / 2, 10))
            confidence = (length_weight * field_score) + ((1 - length_weight) * detail_score)
            if confidence >= hard_threshold:
                if calculated_doc['id'] in duplicate:
                    duplicate[calculated_doc['id']].append(doc['id'])
                else:
                    duplicate[calculated_doc['id']] = [calculated_doc['id'], doc['id']]
                is_duplicate = True
                break
            if confidence >= min_confidence:
                score.append([doc['id'], calculated_doc['id'], confidence])
        if not is_duplicate:
            calculated_docs.append(doc)
        calculate_time += time() - b
    score = sorted(score, key=itemgetter(2), reverse=True)
    medium_score = [s for s in score if s[2] >= soft_threshold]
    weak_score = [s for s in score if s[2] < soft_threshold]
    return duplicate, medium_score, weak_score, tokenize_time, calculate_time
