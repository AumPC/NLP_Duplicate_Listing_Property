import src.Query as Q
import src.ExtractionFilter as Extr
import src.Similarity as Sim
import src.WriteFile as W


QUERY = True
DEBUG = True

TABLE = "condo_listings_dup"


def update(id):
    if DEBUG:
        print("-- Query --")
    if QUERY:
        query_command = "SELECT * FROM " + TABLE + " order by condo_project_id, user_id DESC" #TODO query only updated row
        rows = Q.query(query_command, False, DEBUG)
        if not rows:
            return 'error' #TODO ask protocol with flask
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Extr.extraction(rows, DEBUG)
    if not filter_rows:
        return 'error' #TODO ask protocol with flask
    projects = Extr.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    Q.write_database(projects) #TODO fill this function
    return {} #TODO OK signal


def check_post(request):
    # request should be extract at web api, expect id (str) or request body with necessary field (dict)
    # update system use function update before
    if type(request) == str:
        if DEBUG:
            print("Detect type 'ID', query body from local database")
        query_command = ""  #TODO edit here, query body data if id is given
        request = Q.query(query_command, True, DEBUG)
        if not request:
            return 'error' #TODO ask protocol with flask
    else:
        request = [request]
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("parameter.json")
    query_command = "" #TODO edit here, query all row in request's project_id
    matrix = Q.query(query_command, True, DEBUG)
    query_command = "" #TODO edit here, query vocab set of request's project_id
    vocabulary = Q.query(query_command, True, DEBUG)
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_request = Extr.extraction(request, DEBUG)
    if not filter_request:
        return 'error' #TODO ask protocol with flask
    Sim.tokenize_post(filter_request, vocabulary)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_post(filter_request[0], matrix, parameter)
    if DEBUG:
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
    filter_rows = Extr.extraction(rows, DEBUG)
    projects = Extr.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_all(projects, parameter)
    if DEBUG:
        print(len(strong_duplicate), 'strong-duplicate groups')
        len_of_print = 3 if len(strong_duplicate) > 2 else len(medium_duplicate)
        for i in range(len_of_print):
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
    # results = W.construct_data_frame(rows)
    # results = W.cal_results(results, strong_duplicate, medium_duplicate, weak_duplicate)
    # W.write_results_pickle(results)
    # W.write_results_csv(results)
    #TODO replace result to local database
    return "SUCCESS"


if __name__ == "__main__":
    test_post = '1234'
    result, result_2, result_3 = check_post(test_post)
