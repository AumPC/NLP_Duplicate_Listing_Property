# pip install pythainlp
# pip install python-Levenshtein
import Extraction as Extr
import Similarity as Sim
import QueryFilter as QF
import FindGroup as FG
from pythainlp.tokenize import word_tokenize
# from pythainlp.ner import thainer
from operator import itemgetter
from collections import Counter
from time import time

if __name__ == "__main__":
    print("-- Query --")
    a = time()
    parameter = QF.read_json_file("parameter.json")
    # query_command = "SELECT * FROM condo_listings_sample where id != 576432 order by condo_project_id, user_id DESC limit 100"
    # rows = QF.query(query_command)
    rows = QF.read_json_file("./src/condo_listings_sample.json")
    b = time()
    print('query time:',b-a,'s')
    filter_rows = []
    multiple_row = []
    not_match_row = []
    print("-- Extraction & Filter --")
    for row in rows:
        ext = Extr.extraction(row['detail'])
        if ext == -1:
            multiple_row.append(row)
            continue 
        if ext['price'] != [None, None] and ext['price'] != row['price']:
            not_match_row.append(row)
            continue
        if ext['size'] is not None and ext['size'][0] != '.' and ext['size'][-1] != '.' and float(ext['size']) != row['size']:
            not_match_row.append(row)
            continue
        if ext['tower'] is not None and ext['tower'] != row['tower']:
            not_match_row.append(row)
            continue
        if ext['bedroom'] is not None and ext['bedroom'] != row['bedroom']:
            not_match_row.append(row)
            continue
        if ext['bathroom'] is not None and ext['bathroom'] != row['bathroom']:
            not_match_row.append(row)
            continue
    #     if ext['floor'] is not None and ext['floor'] != row['floor']:
    #         # field not match
    #         continue
    #     if ext['type'] is not None and ext['type'] != row['type']:
    #         # field not match
    #         continue
        row['ext'] = ext
        filter_rows.append(row)

    print("Multiple Context",len(multiple_row),'items')
    print("Not Match Context",len(not_match_row),'items')
    c = time()
    print('extraction time:',c-b,'s')
    rows_group = QF.filter(filter_rows)
    d = time()
    print('filter time:',d-c,'s')
    print("-- Scoring --")
    strong_duplicate = []
    medium_duplicate = []
    weak_duplicate = []
    all_tokenize_time = 0
    all_calculate_time = 0
    all_group_time = 0
    for group in rows_group:
        if len(rows_group[group]) < 2:
            continue
        tokenize_time = 0
        calculate_time = 0
        strong_duplicate_group = {}
        calculated_docs = []
        score = []
        for doc in rows_group[group]:
            is_duplicate = False
            doc['detail_length'] = len(doc['detail'])
            aa = time()
            word_list = word_tokenize(Sim.sampling(doc['detail'], parameter['sampling_rate']), engine='newmm')
            bb = time()
            word_list = {k: v for k, v in Counter(word_list).items() if
                         not (k.isspace() or k.replace('.', '', 1).isdecimal())}
            doc['detail'] = dict(Counter(word_list).most_common(parameter['most_frequency_word']))
            tokenize_time += bb - aa
            for calculated_doc in calculated_docs:
                confidence = Sim.score_calculate(doc, calculated_doc, parameter['weight'])
                if confidence >= parameter['hard_threshold']:
                    if calculated_doc['id'] in strong_duplicate_group:
                        strong_duplicate_group[calculated_doc['id']].append(doc['id'])
                    else:
                        strong_duplicate_group[calculated_doc['id']] = [calculated_doc['id'], doc['id']]
                    is_duplicate = True
                    break
                if confidence >= parameter['min_confidence']:
                    score.append([doc['id'], calculated_doc['id'], confidence])
            if not is_duplicate:
                calculated_docs.append(doc)
            calculate_time += time() - bb
        score = sorted(score, key=itemgetter(2), reverse=True)
        medium_duplicate_pair = [s for s in score if s[2] >= parameter['soft_threshold']]
        weak_duplicate_pair = [s for s in score if s[2] < parameter['soft_threshold']]
        medium_duplicate_group, group_time = FG.group_find(strong_duplicate_group, medium_duplicate_pair)
        strong_duplicate += list(strong_duplicate_group.values())
        medium_duplicate += list(medium_duplicate_group.values())
        weak_duplicate += weak_duplicate_pair
        all_tokenize_time += tokenize_time
        all_calculate_time += calculate_time
        all_group_time += group_time
    weak_duplicate = sorted(weak_duplicate, key=itemgetter(2), reverse=True)
    e = time()
    print('tokenize time:',all_tokenize_time,'s')
    print('calculate score time:',all_calculate_time,'s')
    print('group time:',all_group_time,'s')
    print('total scoring time:',e-d,'s')
    print(len(strong_duplicate), 'strong-duplicate groups')
    for i in range(3):
        print(strong_duplicate[i])
    print(len(medium_duplicate), 'medium-duplicate groups')
    for i in range(3):
        print(medium_duplicate[i])
    print(len(weak_duplicate), 'weak-duplicate pairs')
    for i in range(3):
        print(weak_duplicate[i])
    print('total time:',e-a,'s')
