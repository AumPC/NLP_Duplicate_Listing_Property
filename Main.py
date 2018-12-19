import Extraction as Extr
import Similarity as Sim
import QueryFilter as QF
import FindGroup as FG
from pythainlp.tokenize import word_tokenize
from operator import itemgetter
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas
import pickle


def cal_results(df, sd, md, wd):
    prefix = {"sd": "str_", "md": "med_", "wd": "weak_"}

    for i, row in enumerate(sd):
        group_id = '{}{}'.format(prefix["sd"], i)
        df.loc[row[0]]['is_core_row'] = 1
        for item in row:
            df.loc[item]['s_group_id'] = group_id

    for i, row in enumerate(md):
        group_id = '{}{}'.format(prefix["md"], i)
        df.loc[row[0]]['is_core_row'] = 1
        for item in row:
            df.loc[item]['m_group_id'] = group_id

    for i, row in enumerate(wd):
        group_id = '{}{}'.format(prefix["wd"], i)
        df.loc[row[0]]['is_core_row'] = 1
        for item in row[:2]:
            df.loc[item]['w_group_id'] = group_id

    return df


def write_results_pickle(data):
    with open('results.pkl', 'wb') as f:
        pickle.dump(data, f)

def write_results_csv(data):
    data.to_csv('results.csv')


if __name__ == "__main__":
    print("-- Query --")
    parameter = QF.read_json_file("parameter.json")
    # query_command = "SELECT * FROM condo_listings_sample where id != 576432 order by condo_project_id, user_id DESC"
    # rows = QF.query(query_command)
    rows = QF.read_json_file("./src/condo_listings_sample.json")
    # Start Construct results variable
    df = pandas.DataFrame(rows)
    df.set_index('id', inplace=True)
    results = pandas.DataFrame(columns=['id', 's_group_id', 'm_group_id', 'w_group_id', 'is_core_row'])
    results['id'] = df.index.values
    results.set_index('id', inplace=True)
    # End Construct results variable
    filter_rows = []
    multiple_row = []
    not_match_row = []
    not_found = {'price': 0, 'size': 0, 'tower': 0, 'bedroom': 0, 'bathroom': 0}
    print("-- Extraction & Filter --")
    for row in rows:
        ext = Extr.extraction(row['detail'])
        if ext == -1:
            multiple_row.append(row)
            continue
        if ext['price'] is None:
            not_found['price'] += 1
        if ext['size'] is None:
            not_found['size'] += 1
        if ext['tower'] is None:
            not_found['tower'] += 1
        if ext['bedroom'] is None:
            not_found['bedroom'] += 1
        if ext['bathroom'] is None:
            not_found['bathroom'] += 1
        if ext['price'] is not None and ext['price'] != row['price']:
            not_match_row.append(row)
            continue
        if ext['size'] is not None and ext['size'] != row['size']:
            not_match_row.append(row)
            continue
        if ext['tower'] is not None and ext['tower'] != row['tower']:
            if row['tower'] == '':
                row['tower'] = ext['tower']
            else:
                not_match_row.append(row)
                continue
        if ext['bedroom'] is not None and ext['bedroom'] != row['bedroom']:
            not_match_row.append(row)
            continue
        if ext['bathroom'] is not None and ext['bathroom'] != row['bathroom']:
            not_match_row.append(row)
            continue
        row['ext'] = ext
        filter_rows.append(row)
    print("Not Found Context", not_found)
    print("Multiple Context", len(multiple_row), 'items')
    print("Not Match Context", len(not_match_row), 'items')
    rows_group = QF.filter(filter_rows)
    print("-- Scoring --")
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    for group in rows_group:
        strong_duplicate.append(defaultdict(list))
        medium_duplicate.append([])
        calculated_docs = []
        for doc in rows_group[group]:
            doc['detail'] = doc['title'] + Sim.sampling(doc['detail'], parameter['sampling_rate']) if parameter['sampling_rate'] < 1 else doc['title'] + doc['detail']
        # corpus = CountVectorizer(tokenizer=word_tokenize).fit_transform([doc['detail'] for doc in rows_group[group]]).toarray()
        corpus = TfidfVectorizer(tokenizer=word_tokenize).fit_transform([doc['detail'] for doc in rows_group[group]]).toarray()
        for i in range(len(rows_group[group])):
            rows_group[group][i]['detail'] = corpus[i]
        for doc in rows_group[group]:
            most_confidence, most_duplicate_doc = -1, ''
            for calculated_doc in calculated_docs:
                confidence = Sim.score_calculate(doc, calculated_doc, parameter['weight'], parameter['half_weight_frequency'])
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
        medium_duplicate[-1] = FG.group_find(strong_duplicate[-1], medium_duplicate[-1])
    strong_duplicate = tuple(tuple([k] + v) for sd in strong_duplicate for k, v in sd.items())
    medium_duplicate = tuple(tuple([k] + v) for md in medium_duplicate for k, v in md.items())
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    results = cal_results(results, strong_duplicate, medium_duplicate, weak_duplicate)
    write_results_pickle(results)
    write_results_csv(results)
    print(len(strong_duplicate), 'strong-duplicate groups')
    for i in range(3):
        print(strong_duplicate[i])
    print('...')
    print(len(medium_duplicate), 'medium-duplicate groups')
    len_of_print = 3 if len(medium_duplicate) > 2 else len(medium_duplicate)
    for i in range(len_of_print):
        print(medium_duplicate[i])
    print('...')
    print(len(weak_duplicate), 'weak-duplicate pairs')
    len_of_print = 3 if len(weak_duplicate) > 2 else len(weak_duplicate)
    for i in range(len_of_print):
        print(weak_duplicate[i])
    print('...')
