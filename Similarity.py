import MyCache as C
from Levenshtein import distance
from math import log
from operator import itemgetter
from collections import defaultdict
from itertools import combinations
from copy import deepcopy
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
    union = sum([max(i, j) for i ,j in zip(a, b)])
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


def similarity(projects, group_word_matrix, parameter):
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    for project in projects.values():
        project_id = project[0]['project']
        strong_duplicate_pairs = []
        medium_duplicate_pairs = []
        for i, doc in enumerate(project):
            doc['detail'] = group_word_matrix[project_id][i]
        calculated_docs = [(a['id'], b['id'], score_calculate(a, b, parameter['weight'], parameter['half_weight_frequency'])) for a, b in combinations(project, 2)]
        most_confidences = {i['id']: (i['id'], 0) for i in project}
        for a, b, score in calculated_docs:
            if most_confidences[a][1] < score:
                most_confidences[a] = (b, score)
            if most_confidences[b][1] < score:
                most_confidences[b] = (a, score)
        for doc, most_confidence in most_confidences.items():
            if most_confidence[1] >= parameter['hard_threshold']:
                strong_duplicate_pairs.append((doc, most_confidence[0]))
            elif most_confidence[1] >= parameter['soft_threshold']:
                medium_duplicate_pairs.append((doc, most_confidence[0]))
            elif most_confidence[1] >= parameter['min_confidence']:
                weak_duplicate.append((doc, most_confidence[0], most_confidence[1]))
        strong_duplicate.append(group_find(strong_duplicate_pairs))
        medium_duplicate.append(group_find(medium_duplicate_pairs, strong_duplicate[-1]))
    strong_duplicate = tuple(tuple([k] + v) for sd in strong_duplicate for k, v in sd.items())
    medium_duplicate = tuple(tuple([k] + v) for md in medium_duplicate for k, v in md.items())
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    return strong_duplicate, medium_duplicate, weak_duplicate


def tokenize(projects, DEBUG):
    group_word_matrix = {}
    try:
        group_word_matrix = C.load_pickle('group_word_matrix', DEBUG)
        if DEBUG:
            print("Use cached \"group_word_matrix\"")
    except FileNotFoundError:
        if DEBUG:
            print("Calculate \"group_word_matrix\"")
        for project in projects.values():
            project_id = project[0]['project']
            matrix = TfidfVectorizer(tokenizer=word_tokenize).fit_transform([doc['title'] + doc['detail'] for doc in project]).toarray()
            group_word_matrix[project_id] = matrix
        C.create_pickle('group_word_matrix', group_word_matrix, DEBUG)
    return group_word_matrix


if __name__ == '__main__':
    test_pair = [(1, 2),
                 (1, 3),
                 (1, 4),
                 (2, 3),
                 (2, 4),
                 (3, 4)]
    group = group_find(test_pair)
    print(group)
    for g in group:
        print(group[g])
