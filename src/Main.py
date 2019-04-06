from flask.json import jsonify
import src.Query as Q
import src.ExtractionFilter as Extr
import src.Similarity as Sim


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


def clone():
    if DEBUG:
        print("-- Query --")
    if QUERY:
        query_command = "SELECT * FROM " + TABLE + " order by condo_project_id"  # TODO query only "parent"
        rows = Q.query(query_command, False, DEBUG)
        if not rows:
            return 'ERROR: Renthub database give nothing', 404
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Extr.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Extr.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    Q.write_database('projects', projects, DEBUG)
    return 'success'


def update(id):
    if DEBUG:
        print("-- Query --")
    if QUERY:
        query_command = ""  # TODO query this id from global
        rows = Q.query(query_command, False, DEBUG)
        if not rows:
            return 'ERROR: Renthub database give nothing', 404
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Extr.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    Sim.tokenize_post(filter_rows, DEBUG)
    Q.write_database('projects',filter_rows , DEBUG)
    return 'success'


def check_post(request):
    if type(request) == str:
        if DEBUG:
            print("Detect type 'ID', query body from local database")
        query_command = ""  # TODO edit here, query body data if id is given
        request = Q.query(query_command, True, DEBUG)
        if not request:
            return 'ERROR: Service database give no request body', 404
    else:
        request = [request]
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("parameter.json")
    query_command = ""  # TODO edit here, query all row in request's project_id
    matrix = Q.query(query_command, True, DEBUG)
    if not request:
        return 'ERROR: Service database give no matrix', 404
    query_command = ""  # TODO edit here, query corpus of request's project_id
    corpus = Q.query(query_command, True, DEBUG)
    if not request:
        return 'ERROR: Service database give no corpus', 404
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_request = Extr.extraction(request, DEBUG)
    if not filter_request:
        return 'ERROR: All row are multiple content or not-matched content', 401
    Sim.tokenize_post(filter_request, corpus)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_post(filter_request[0], matrix, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return jsonify({'strong_duplicate': strong_duplicate, 'medium_duplicate': medium_duplicate, 'weak_duplicate': weak_duplicate})


def check_all():
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("parameter.json")
    if QUERY:
        query_command = "SELECT * FROM " + TABLE + " order by condo_project_id, user_id DESC"  # TODO query only "parent"
        rows = Q.query(query_command, False, DEBUG)
        if not rows:
            return 'ERROR: Renthub database give nothing', 404
    else:
        rows = Q.read_json_file("./data/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Extr.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Extr.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_all(projects, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return jsonify({'strong_duplicate': strong_duplicate, 'medium_duplicate': medium_duplicate, 'weak_duplicate': weak_duplicate})


if __name__ == "__main__":
    test_post = '1234'
    result, result_2, result_3 = check_post(test_post)
