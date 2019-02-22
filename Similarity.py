import MyCache as C
from Levenshtein import distance
from math import log
from operator import itemgetter
from collections import defaultdict
from copy import deepcopy
from pythainlp.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


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
    intersect = sum([min(a[i], b[i]) for i in range(len(a))])
    union = sum([max(a[i], b[i]) for i in range(len(a))])
    return (1+intersect)/(1+union)


def score_calculate(a, b, weight, half_weight_frequency):
    field_score = field_similarity(a, b, weight)
    detail_score = detail_similarity(a['detail'], b['detail'])
    length_weight = 1 / (1 + log(1 + (sum(a['detail']) + sum(b['detail'])) / 2, half_weight_frequency + 1))
    return (length_weight * field_score) + ((1 - length_weight) * detail_score)


def group_find(group, score):
    expand_group = defaultdict(list, deepcopy(group))
    ans = {i: i for i in {s[0] for s in score}.union({s[1] for s in score})}
    for i in score:
        while ans[i[0]] != ans[ans[i[0]]]:
            ans[i[0]] = ans[ans[i[0]]]
        while ans[i[1]] != ans[ans[i[1]]]:
            ans[i[1]] = ans[ans[i[1]]]
        ans[i[0]] = ans[i[1]]
    for i in ans:
        while ans[i] != ans[ans[i]]:
            ans[i] = ans[ans[i]]
        if i == ans[i]:
            continue
        expand_group[ans[i]].append(i)
    return expand_group


def similarity(groups, group_word_matrix, parameter):
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []

    for group in groups.values():
        project_id = group[0]['project']
        strong_duplicate.append(defaultdict(list))
        medium_duplicate.append([])
        calculated_docs = []

        for i, doc in enumerate(group):
            doc['detail'] = group_word_matrix[project_id][i]

        for doc in group:
            most_confidence, most_duplicate_doc = -1, ''
            for calculated_doc in calculated_docs:
                confidence = score_calculate(doc, calculated_doc, parameter['weight'],
                                                 parameter['half_weight_frequency'])
                if confidence > most_confidence:
                    most_confidence, most_duplicate_doc = confidence, calculated_doc['id']
                if most_confidence >= parameter['hard_threshold']:
                    strong_duplicate[-1][calculated_doc['id']].append(doc['id'])
                    break
            if most_confidence < parameter['hard_threshold']:
                calculated_docs.append(doc)
                if most_confidence >= parameter['soft_threshold']:
                    medium_duplicate[-1].append((doc['id'], most_duplicate_doc, most_confidence))
                elif most_confidence >= parameter['min_confidence']:
                    weak_duplicate.append((doc['id'], most_duplicate_doc, most_confidence))
        medium_duplicate[-1] = group_find(strong_duplicate[-1], medium_duplicate[-1])
    strong_duplicate = tuple(tuple([k] + v) for sd in strong_duplicate for k, v in sd.items())
    medium_duplicate = tuple(tuple([k] + v) for md in medium_duplicate for k, v in md.items())
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    return strong_duplicate, medium_duplicate, weak_duplicate


def tokenize(groups, DEBUG):
    group_word_matrix = {}
    try:
        group_word_matrix = C.load_pickle('group_word_matrix', DEBUG)
        if DEBUG:
            print("Use cached \"group_word_matrix\"")
    except:
        if DEBUG:
            print("Calculate \"group_word_matrix\"")
        for group in groups.values():
            project_id = group[0]['project']
            matrix = TfidfVectorizer(tokenizer=word_tokenize).fit_transform([doc['title'] + doc['detail'] for doc in group]).toarray()
            group_word_matrix[project_id] = matrix
        C.create_pickle('group_word_matrix', group_word_matrix, DEBUG)
    return group_word_matrix


if __name__ == '__main__':
    test_score = [[1, 2, 0.6],
                  [1, 3, 0.2],
                  [1, 4, 0.1],
                  [2, 3, 0.3],
                  [2, 4, 0.1],
                  [3, 4, 0.5]]
    group, time = group_find({}, test_score)
    print(group)
    for g in group:
        print(group[g])
