import Extraction as Extr
import Similarity as Sim
import QueryFilter as QF
import FindGroup as FG
# from time import time

if __name__ == "__main__":
    print("-- Query --", '\n')
    # a = time()
    parameter = QF.read_json_file("parameter.json")
    # query_command = "SELECT * FROM condo_listings_sample where id != 576432 order by condo_project_id, user_id DESC limit 100"
    # rows = QF.query(query_command)
    rows = QF.read_json_file("./src/condo_listings_sample.json")
    # b = time()
    # print(b-a)
    filter_rows = []
    multiple_row = []
    not_match_row = []
    print("-- Extraction & Filter--", '\n')
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

    print("Multiple Context", len(multiple_row), '\n')
    print("Not Match Context", len(not_match_row), '\n')
    # c = time()
    # print(c-b)
    rows_group = QF.filter(filter_rows)
    # d = time()
    # print(d-c)
    print("-- Scoring --", '\n')
    score = []
    for group in rows_group:
        if len(rows_group[group]) < 2:
            continue
        score += Sim.score_calculate(rows_group[group], parameter['weight'], parameter['min_confidence'])
    # e = time()
    # print(e-d)
    group = FG.group_find(score, parameter['min_cluster_similarity'])
    # for g in group:
    #     if len(group[g]) > 1:
    #         print(group[g])
    # f = time()
    # print(f-e)
    # print('total', f-a)
