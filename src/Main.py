import src.Query as Q
import src.ExtractionFilter as Extr
import src.Similarity as Sim
import src.WriteFile as W


QUERY = True
DEBUG = True

TABLE = "condo_listings_dup"
EXTRACTED_TABLE = "condo_listings_dup"


def print_group(strong_duplicate, medium_duplicate, weak_duplicate):
    print(len(strong_duplicate), 'strong-duplicate docs')
    len_of_print = 3 if len(strong_duplicate) > 2 else len(medium_duplicate)
    for i in range(len_of_print):
        print(strong_duplicate[i])
    print('...')
    print(len(medium_duplicate), 'medium-duplicate docs')
    len_of_print = 3 if len(medium_duplicate) > 2 else len(medium_duplicate)
    for i in range(len_of_print):
        print(medium_duplicate[i])
    print('...')
    print(len(weak_duplicate), 'weak-duplicate docs')
    len_of_print = 3 if len(weak_duplicate) > 2 else len(weak_duplicate)
    for i in range(len_of_print):
        print(weak_duplicate[i])
    print('...')

def update():
    # version 1 : query all, replace to local database all
    if DEBUG:
        print("-- Query --")
    if QUERY:
        query_command = "SELECT * FROM " + TABLE + " order by condo_project_id, user_id DESC"
        rows = Q.query(query_command, False, DEBUG)
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows, multiple_row, check_floor_row, not_match_row, not_found = Extr.extraction(rows, DEBUG)
    projects = Extr.group_by_project(filter_rows)
    Sim.tokenize_new(projects)
    Q.write_database(projects) #TODO fill this function
    return {}


def create_update_id(id):
    # Q.create_table('extracted_table', DEBUG)
    Q.write_database('extracted_table', [], DEBUG)
    return ''


def delete_id(id):
    return {}


def check_post(request):
    # request should be extract at web api, expect id (int) or request body with necessary field (dict)
    # update system use function update below
    if type(request) == int:
        if DEBUG:
            print("Detect type 'ID', query body from local database")
        query_command = ""  #TODO edit here, query body data if id is given
        request = Q.query(query_command, True, DEBUG)[0] #TODO bug if result is none
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("../parameter.json")
    query_command = "" #TODO edit here, query all row in request's project_id
    matrix = Q.query(query_command, True, DEBUG)
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows, multiple_row, check_floor_row, not_match_row, not_found = Extr.extraction([request], DEBUG) # should we extract this?
    if not filter_rows:
        return 'error'
    request = Sim.tokenize_request(filter_rows, matrix) #TODO tfidf config?
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_req(request, matrix, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return strong_duplicate, medium_duplicate, weak_duplicate


def check_all():
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("parameter.json")
    if QUERY:
        query_command = "SELECT * FROM " + TABLE + " order by condo_project_id, user_id DESC"
        rows = Q.query(query_command, False, DEBUG)
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows, multiple_row, check_floor_row, not_match_row, not_found = Extr.extraction(rows, DEBUG)
    projects = Extr.group_by_project(filter_rows)
    group_word_matrix = Sim.tokenize(projects, DEBUG)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_all(projects, group_word_matrix, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    results = W.construct_data_frame(rows)
    results = W.cal_results(results, strong_duplicate, medium_duplicate, weak_duplicate)
    W.write_results_pickle(results)
    W.write_results_csv(results)
    # return results
    return "SUCCESS"


if __name__ == "__main__":
    test_post = '1234'
    result, result_2, result_3 = check_post(test_post)
