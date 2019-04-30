import pandas
import pickle
import json
import os


def save_to_file(data, filename):
    open_file = open(filename, 'w')
    json.dump(data, open_file, sort_keys=True, indent=4)
    open_file.close()


def construct_data_frame(rows):
    df = pandas.DataFrame(rows)
    df.set_index('id', inplace=True)
    results = pandas.DataFrame(columns=['id', 's_group_id', 'm_group_id', 'w_group_id', 'is_core_row'])
    results['id'] = df.index.values
    results.set_index('id', inplace=True)
    return results


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


def write_results_pickle(data, file='result_group.pkl'):
    if not os.path.exists("results/"):
        os.mkdir("results/")
    with open('results/' + file, 'wb') as f:
        pickle.dump(data, f)


def write_results_csv(data, file='results/result_group.csv'):
    data.to_csv(file)
