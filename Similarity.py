# pip install pythainlp
from pythainlp.tokenize import word_tokenize
# from pythainlp.ner import thainer
from math import log


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


def field_similarity(pair, weight):
    price_score = weight['price'] * different_numerical(pair[0]['price'][0], pair[1]['price'][0])
    size_score = weight['size'] * different_numerical(pair[0]['size'], pair[1]['size'])
    tower_score = weight['tower'] * different_character(pair[0]['tower'], pair[1]['tower'])
    floor_score = weight['floor'] * different_character(pair[0]['floor'], pair[1]['floor'])
    type_score = weight['type'] * different_character(pair[0]['type'], pair[1]['type'])
    return price_score + size_score + tower_score + floor_score + type_score


def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def bag_of_word(text):
    word_list = word_tokenize(text, engine='newmm')
    bag = {}
    for word in word_list:
        if word == ' ' or word == '\n' or is_number(word):
            continue
        elif word in bag:
            bag[word] += 1
        else:
            bag[word] = 1
    return bag


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


def score_calculate(docs, weight, min_confidence):
    score = []
    for doc in docs:
        doc['detail_length'] = len(doc['detail'])
        doc['detail'] = bag_of_word(doc['detail'])
    for first in range(len(docs) - 1):
        for second in range(first + 1, len(docs)):
            field_score = field_similarity([docs[first], docs[second]], weight)
            detail_score = detail_similarity(docs[first]['detail'], docs[second]['detail'])
            length_weight = 1 / (1 + log(1 + (docs[first]['detail_length'] + docs[second]['detail_length']) / 2, 10))
            confidence = (length_weight * field_score) + ((1 - length_weight) * detail_score)
            if confidence >= min_confidence:
                score.append([docs[first]['id'], docs[second]['id'], confidence])
    return score
