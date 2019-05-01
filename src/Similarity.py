from Levenshtein import distance
from math import log
from operator import itemgetter
from collections import defaultdict
from itertools import combinations
from copy import deepcopy
from pythainlp.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import src.Query as Query
import src.WriteFile as Write
import numpy


def different_numerical(a, b):
    try:
        return min(1 - (abs(a - b) * 2 / (a + b)), 0)
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
        price_score = weight['price'] * (different_numerical(a['price'][0], b['price'][0]) + different_numerical(a['price'][1], b['price'][1])) / 2
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


def group_find(pairs, default_group=None):
    if default_group is None:
        group = defaultdict(list)
    else:
        group = defaultdict(list, deepcopy(default_group))
    ans = {i: i for i in {a for a, b in pairs}.union({b for a, b in pairs})}
    for a, b in pairs:
        while ans[a] != ans[ans[a]]:
            ans[a] = ans[ans[a]]
        while ans[b] != ans[ans[b]]:
            ans[b] = ans[ans[b]]
        ans[a] = ans[b]
    for i in ans:
        while ans[i] != ans[ans[i]]:
            ans[i] = ans[ans[i]]
        if i == ans[i]:
            continue
        group[ans[i]].append(i)
    return group


def similarity_post(request, matrix, parameter):
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    scores = [(doc['id'], score_calculate(request, doc, parameter['weight'], parameter['half_weight_frequency'])) for doc in matrix if doc['id'] != request['id']]
    for doc, score in scores:
        if score >= parameter['strong_threshold']:
            strong_duplicate.append((doc, score))
        elif score >= parameter['medium_threshold']:
            medium_duplicate.append((doc, score))
        elif score >= parameter['weak_threshold']:
            weak_duplicate.append((doc, score))
    strong_duplicate = sorted(strong_duplicate, key=itemgetter(1), reverse=True)
    medium_duplicate = sorted(medium_duplicate, key=itemgetter(1), reverse=True)
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(1), reverse=True)
    return strong_duplicate, medium_duplicate, weak_duplicate


def similarity_all(projects, parameter):
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    most_confidences = {}
    threshold_check = []
    for project_id, project in projects.items():
        calculated_docs = [(a['id'], b['id'], a['threshold_check'], b['threshold_check'], score_calculate(a, b, parameter['weight'], parameter['half_weight_frequency'])) for a, b in combinations(project, 2)]
        most_confidences[project_id] = {i['id']: (i['id'], 0) for i in project}
        for a, b, threshold_check_a, threshold_check_b, score in calculated_docs:
            if most_confidences[project_id][a][1] < score:
                most_confidences[project_id][a] = (b, score)
            if most_confidences[project_id][b][1] < score:
                most_confidences[project_id][b] = (a, score)
            threshold_check.append((score, threshold_check_a, threshold_check_b))
    if parameter['auto_threshold']:
        threshold_calculate(threshold_check, parameter)
    for project_id in projects:
        strong_duplicate_pairs = []
        medium_duplicate_pairs = []
        for doc, most_confidence in most_confidences[project_id].items():
            if most_confidence[1] >= parameter['strong_threshold']:
                strong_duplicate_pairs.append((doc, most_confidence[0]))
            elif most_confidence[1] >= parameter['medium_threshold']:
                medium_duplicate_pairs.append((doc, most_confidence[0]))
            elif most_confidence[1] >= parameter['weak_threshold']:
                weak_duplicate.append((doc, most_confidence[0], most_confidence[1]))
        strong_duplicate.append(group_find(strong_duplicate_pairs))
        medium_duplicate.append(group_find(medium_duplicate_pairs, strong_duplicate[-1]))
    strong_duplicate = tuple(tuple([k] + v) for sd in strong_duplicate for k, v in sd.items())
    medium_duplicate = tuple(tuple([k] + v) for md in medium_duplicate for k, v in md.items())
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    return strong_duplicate, medium_duplicate, weak_duplicate


def tokenize_all(projects, idf, debug):
    if debug:
        print("Calculate \"group_word_matrix\"")
    corpus = []
    for project in projects.values():
        if debug:
            print("Tokenize project", project[0]['project'])
        vectorizer = CountVectorizer(tokenizer=word_tokenize)
        tokenized = vectorizer.fit_transform([doc['title'] + doc['detail'] for doc in project])
        if idf:
            matrix = TfidfTransformer().fit_transform(tokenized).toarray()
        else:
            matrix = tokenized.toarray()
        for i, doc in enumerate(project):
            doc['threshold_check'] = doc['title'] + doc['detail'][:100] if len(doc['detail']) > 100 else doc['title'] + doc['detail']
            doc['detail'] = matrix[i]
        if project[0]['project'] is not None:
            corpus.append({'id': project[0]['project'], 'project': project[0]['project'], 'corpus': vectorizer.get_feature_names()})
        else:
            corpus.append({'id': 0, 'project': None, 'corpus': vectorizer.get_feature_names()})
    Query.write_database('corpus', corpus, debug)


def tokenize_post(request, matrix, vocabulary, idf):
    tokenized = CountVectorizer(tokenizer=word_tokenize, vocabulary=vocabulary).fit_transform([request[0]['title'] + request[0]['detail']])
    if idf:
        transformer = TfidfTransformer()
        transformed = transformer.fit_transform([doc['detail'] for doc in matrix]).toarray()
        for i, doc in enumerate(matrix):
            doc['detail'] = transformed[i]
        request[0]['detail'] = transformer.transform(tokenized).toarray()[0]
    else:
        request[0]['detail'] = tokenized.toarray()


def transform_post(request, matrix):
    transformer = TfidfTransformer()
    transformed = transformer.fit_transform([doc['detail'] for doc in matrix]).toarray()
    for i, doc in enumerate(matrix):
        doc['detail'] = transformed[i]
    request[0]['detail'] = transformer.transform([request[0]['detail']]).toarray()[0]


def threshold_calculate(pairs, parameter):
    duplicate_pairs = []
    strong_threshold = 0
    previous_difference = 0
    for pair in pairs:
        if pair[1] == pair[2]:
            duplicate_pairs.append(pair[0])
        elif pair[0] > strong_threshold:
            strong_threshold = pair[0]
    parameter['strong_threshold'] = strong_threshold
    duplicate_range_count = [0] * parameter['data_range']
    for score in duplicate_pairs:
        i = parameter['data_range'] - 1
        while i / parameter['data_range'] > score:
            i -= 1
        duplicate_range_count[parameter['data_range'] - i - 1] += 1
    for i in range(len(duplicate_range_count) - 1):
        difference = duplicate_range_count[i] - duplicate_range_count[i + 1]
        if previous_difference > difference:
            parameter['medium_threshold'] = min((parameter['data_range'] - i - 0.5) / parameter['data_range'], parameter['strong_threshold'])
            break
        previous_difference = difference
    parameter['weak_threshold'] = min(numpy.percentile(duplicate_pairs, parameter['tail_percentile']), parameter['medium_threshold'])
    Write.save_to_file(parameter, 'parameter.json')
