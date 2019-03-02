from Levenshtein import distance
from math import log
from operator import itemgetter
from pythainlp.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


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
    intersect = sum([min(i, j) for i, j in zip(a, b)])
    union = sum([max(i, j) for i, j in zip(a, b)])
    return (1+intersect)/(1+union)


def score_calculate(a, b, weight, half_weight_frequency):
    field_score = field_similarity(a, b, weight)
    detail_score = detail_similarity(a['detail'], b['detail'])
    length_weight = 1 / (1 + log(1 + (sum(a['detail']) + sum(b['detail'])) / 2, half_weight_frequency + 1))
    return (length_weight * field_score) + ((1 - length_weight) * detail_score)


def similarity(request, matrix, parameter):
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    scores = [(doc['id'], score_calculate(request, doc, parameter['weight'], parameter['half_weight_frequency'])) for doc in matrix]
    for doc, score in scores:
        if score >= parameter['hard_threshold']:
            strong_duplicate.append((doc, score))
        elif score >= parameter['soft_threshold']:
            medium_duplicate.append((doc, score))
        elif score >= parameter['min_confidence']:
            weak_duplicate.append((doc, score))
    strong_duplicate = sorted(strong_duplicate, key=itemgetter(2), reverse=True)
    medium_duplicate = sorted(medium_duplicate, key=itemgetter(2), reverse=True)
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    return strong_duplicate, medium_duplicate, weak_duplicate


def tokenize(projects):
    for project in projects.values():
        matrix = TfidfVectorizer(tokenizer=word_tokenize).fit_transform([doc['title'] + doc['detail'] for doc in project]).toarray()
        for i, doc in enumerate(project):
            doc['detail'] = matrix[i]


def tokenize_request(request, matrix):
    corpus = [doc['title'] + doc['detail'] for doc in matrix]
    corpus.append(request[0]['title'] + request[0]['detail'])
    request[0]['detail'] = TfidfVectorizer(tokenizer=word_tokenize).fit_transform(corpus).toarray()[-1]
    return request[0]
