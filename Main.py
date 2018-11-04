import Extraction as Extr
import Similarity as Sim
import QueryFilter as QF

from math import log

if __name__ == "__main__":
    print("-- Query --", '\n')
    WEIGHT = {'price':0.2, 'size':0.2, 'tower':0.2, 'floor':0.2, 'type':0.2} # tune here
    rows = QF.query()
    filter_rows = []
    print("-- Extraction & Filter--", '\n')
    for row in rows:
        # print('---------------------------------------------------------------------------\n',row['id'],'\n')
        ext = Extr.extraction(row['detail'])

    #     if ext['price'] != None and ext['price'] != row['price']:
    #         # field not match
    #         continue
    #     if ext['size'] != None and ext['size'] != row['size']:
    #         # field not match
    #         continue
    #     if ext['tower'] != None and ext['tower'] != row['tower']:
    #         # field not match
    #         continue
    #     if ext['floor'] != None and ext['floor'] != row['floor']:
    #         # field not match
    #         continue
    #     if ext['type'] != None and ext['type'] != row['type']:
    #         # field not match
    #         continue
        row['ext'] = ext
        filter_rows.append(row)

    rows_pair = QF.filter(filter_rows)

    print("-- Scoring --", '\n')
    score = []
    for pairs in rows_pair:
        if len(pairs) < 2:
            continue
        for first in range(len(pairs)-1):
            for second in range(len(pairs)-first-1):
                sec = first + second + 1
                field_score = Sim.field_similarity([pairs[first],pairs[sec]], WEIGHT)
                detail_score = Sim.detail_similarity(pairs[first]['detail'], pairs[sec]['detail'])
                length_weight = 1/(1 + log(1 + (len(pairs[first]['detail']) + len(pairs[sec]['detail']))/2, 10))
                confidence = (length_weight * field_score) + ((1 - length_weight) * detail_score)
                if confidence > 0:
                    # tune threshold here
                    score.append([pairs[first]['id'], pairs[sec]['id'], confidence])
    for s in score:
        print(s)