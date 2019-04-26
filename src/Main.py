from flask.json import jsonify
import src.Query as Query
import src.ExtractionFilter as Ext
import src.Similarity as Sim
import src.WriteFile as Write


DEBUG = True
GLOBAL_TABLE = "condo_listings_sample"


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
    query_command = f"SELECT * FROM {GLOBAL_TABLE} WHERE parent_id IS NULL ORDER BY condo_project_id DESC"  # TODO check "parent"'s parent
    rows = Query.query(query_command, False, DEBUG)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Ext.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Ext.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    Query.write_database('projects', projects, DEBUG)
    return 'success'


def update(update_id):
    if DEBUG:
        print("-- Query --")
    query_command = f"SELECT * FROM {GLOBAL_TABLE} WHERE id = {update_id}"
    rows = Query.query(query_command, False, DEBUG)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    query_command = f"SELECT corpus FROM public.corpus WHERE condo_project_id = {rows[0]['condo_project_id']}"
    corpus = Query.query(query_command, True, DEBUG)
    if not corpus:
        return 'ERROR: Service database give no corpus', 404
    else:
        corpus = corpus[0]['corpus']
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Ext.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    Sim.tokenize_post(filter_rows, corpus)
    Query.write_database('projects', filter_rows, DEBUG)
    return 'success'


def check_post(request):
    if type(request) == int:
        if DEBUG:
            print("Detect type 'ID', query body from local database")
        query_command = f"SELECT * FROM public.projects WHERE id = {request}"
        request_body = Query.query(query_command, True, DEBUG)
        if not request_body:
            return 'ERROR: Service database give no request body', 404
    else:
        request_body = [request]
    if DEBUG:
        print("-- Query --")
    parameter = Query.read_json_file("parameter.json")
    query_command = f"SELECT * FROM {GLOBAL_TABLE} WHERE condo_project_id = {request_body[0]['condo_project_id']}"
    matrix = Query.query(query_command, True, DEBUG)
    if not matrix:
        return 'ERROR: Service database give no matrix', 404
    query_command = f"SELECT corpus FROM public.corpus WHERE condo_project_id = {request_body[0]['condo_project_id']}"
    corpus = Query.query(query_command, True, DEBUG)
    if not corpus:
        return 'ERROR: Service database give no corpus', 404
    else:
        corpus = corpus[0]['corpus']
    if DEBUG:
        print("-- Extraction & Filter --")
    if type(request) == int:
        filter_request = request_body
    else:
        filter_request = Ext.extraction(request_body, DEBUG)
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
    parameter = Query.read_json_file("parameter.json")
    query_command = f"SELECT * FROM {GLOBAL_TABLE} WHERE parent_id IS NULL ORDER BY condo_project_id DESC"  # TODO check "parent"'s parent
    rows = Query.query(query_command, False, DEBUG)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows = Ext.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Ext.group_by_project(filter_rows)
    Sim.tokenize_all(projects, DEBUG)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_all(projects, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return jsonify({'strong_duplicate': strong_duplicate, 'medium_duplicate': medium_duplicate, 'weak_duplicate': weak_duplicate})


def get_parameter():
    return jsonify(Query.read_json_file("parameter.json"))


def set_parameter(data):
    parameter = Query.read_json_file("parameter.json")
    for field in data:
        if field == 'weight':
            for weight in data[field]:
                if weight in parameter[field] and isinstance(parameter[field][weight], type(data[field][weight])):
                    parameter[field][weight] = data[field][weight]
                else:
                    return 'ERROR: invalid data type', 401
        elif field in parameter and isinstance(parameter[field], type(data[field])):
            parameter[field] = data[field]
        else:
            return 'ERROR: invalid data type', 401
    Write.save_to_file(parameter, 'parameter.json')
    return 'success'


if __name__ == "__main__":
    test_post = '1234'
    result, result_2, result_3 = check_post(test_post)
