from flask.json import jsonify
import src.Query as Query
import src.ExtractionFilter as Ext
import src.Similarity as Sim
import src.WriteFile as Write


DEBUG = True


def print_group(strong_duplicate, medium_duplicate, weak_duplicate):
    print(len(strong_duplicate), 'strong-duplicate docs')
    len_of_print = 3 if len(strong_duplicate) > 2 else len(strong_duplicate)
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


def clone(debug=DEBUG):
    if debug:
        print("-- Query --")
    query_command = ["SELECT * FROM ", " WHERE parent_id IS NULL ORDER BY condo_project_id DESC"]
    rows = Query.query(query_command, False, debug)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    if debug:
        print("-- Extraction & Filter --")
    filter_rows, multiple_rows, mismatch_rows = Ext.extraction(rows, debug)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Ext.group_by_project(filter_rows)
    Sim.tokenize_all(projects, False, debug)
    Query.write_database('projects', projects, debug)
    return jsonify({'multiple': multiple_rows, 'mismatch': mismatch_rows})


def update(update_id):
    if DEBUG:
        print("-- Query --")
    query_command = ["SELECT * FROM ", f" WHERE id = {update_id}"]
    rows = Query.query(query_command, False, DEBUG)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    if rows[0]['project'] is not None:
        query_command = f"SELECT * FROM public.projects WHERE project = {rows[0]['project']}"
    else:
        query_command = "SELECT * FROM public.projects WHERE project is null"
    matrix = Query.query(query_command, True, DEBUG)
    if not matrix:
        return 'ERROR: Service database give no matrix', 404
    if rows[0]['project'] is not None:
        query_command = f"SELECT corpus FROM public.corpus WHERE project = {rows[0]['project']}"
    else:
        query_command = f"SELECT corpus FROM public.corpus WHERE project is null"
    corpus = Query.query(query_command, True, DEBUG)
    if not corpus:
        return 'ERROR: Service database give no corpus', 404
    else:
        corpus = corpus[0]['corpus']
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows, multiple_rows, mismatch_rows = Ext.extraction(rows, DEBUG)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    Sim.tokenize_post(filter_rows, matrix, corpus, False)
    Query.write_database('projects', filter_rows, DEBUG)
    return jsonify({'multiple': multiple_rows, 'mismatch': mismatch_rows})


def check_post(request):
    if type(request) == int:
        if DEBUG:
            print("Detect type 'ID', query body from local database")
        query_command = f"SELECT * FROM public.projects WHERE id = {request}"
        request_body = Query.query(query_command, True, DEBUG)
        if not request_body:
            return 'ERROR: Service database give no request body', 404
    else:
        request['bedroom'] = Query.process_bed_bath(request['tower'])
        request['bathroom'] = Query.process_bed_bath(request['tower'])
        request['tower'] = Query.process_tower(request['tower'])
        request['floor'] = Query.process_floor(request['floor'])
        request['detail'] = Query.process_detail(request['detail'])
        request_body = [request]
    if DEBUG:
        print("-- Query --")
    parameter = Query.read_json_file("parameter.json")
    if request_body[0]['project'] is not None:
        query_command = f"SELECT * FROM public.projects WHERE project = {request_body[0]['project']}"
    else:
        query_command = "SELECT * FROM public.projects WHERE project is null"
    matrix = Query.query(query_command, True, DEBUG)
    if not matrix:
        return 'ERROR: Service database give no matrix', 404
    if request_body[0]['project'] is not None:
        query_command = f"SELECT corpus FROM public.corpus WHERE project = {request_body[0]['project']}"
    else:
        query_command = "SELECT corpus FROM public.corpus WHERE project is null"
    corpus = Query.query(query_command, True, DEBUG)
    if not corpus:
        return 'ERROR: Service database give no corpus', 404
    else:
        corpus = corpus[0]['corpus']
    if DEBUG:
        print("-- Extraction & Filter --")
    if type(request) == int:
        filter_request, multiple_rows, mismatch_rows = request_body, [], []
        Sim.transform_post(filter_request, matrix)
    else:
        filter_request, multiple_rows, mismatch_rows = Ext.extraction(request_body, DEBUG)
        if not filter_request:
            return 'ERROR: All row are multiple content or not-matched content', 401
        Sim.tokenize_post(filter_request, matrix, corpus, True)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_post(filter_request[0], matrix, parameter)
    if DEBUG:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return jsonify({'strong_duplicate': strong_duplicate, 'medium_duplicate': medium_duplicate, 'weak_duplicate': weak_duplicate, 'multiple': multiple_rows, 'mismatch': mismatch_rows})


def check_all(debug=DEBUG):
    if debug:
        print("-- Query --")
    parameter = Query.read_json_file("parameter.json")
    query_command = ["SELECT * FROM ", " WHERE parent_id IS NULL ORDER BY condo_project_id DESC"]
    rows = Query.query(query_command, False, debug)
    if not rows:
        return 'ERROR: Renthub database give nothing', 404
    if debug:
        print("-- Extraction & Filter --")
    filter_rows, multiple_rows, mismatch_rows = Ext.extraction(rows, debug)
    if not filter_rows:
        return 'ERROR: All row are multiple content or not-matched content', 401
    projects = Ext.group_by_project(filter_rows)
    Sim.tokenize_all(projects, True, debug)
    if debug:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity_all(projects, parameter)
    if debug:
        print_group(strong_duplicate, medium_duplicate, weak_duplicate)
    return jsonify({'strong_duplicate': strong_duplicate, 'medium_duplicate': medium_duplicate, 'weak_duplicate': weak_duplicate, 'multiple': multiple_rows, 'mismatch': mismatch_rows})


def get_parameter():
    return jsonify(Query.read_json_file("parameter.json"))


def set_parameter(data):
    parameter = Query.read_json_file("parameter.json")
    for field in data:
        if field == 'weight':
            for weight in data[field]:
                if weight not in parameter[field]:
                    return f'ERROR: invalid {field} field name', 401
                if not (isinstance(data[field][weight], float) or isinstance(data[field][weight], int)):
                    return f'ERROR: invalid {field} type: expect int or float', 401
                if not 0 <= data[field][weight] <= 1:
                    return f'ERROR: invalid {field} range', 401
                parameter[field][weight] = data[field][weight]
        elif field == 'data_range' or field == 'half_weight_frequency':
            if not isinstance(data[field], int):
                return f'ERROR: invalid {field} type: expect int', 401
            if data[field] < 1:
                return f'ERROR: invalid {field} range', 401
            parameter[field] = data[field]
        elif field == 'tail_percentile':
            if not (isinstance(data[field], float) or isinstance(data[field], int)):
                return f'ERROR: invalid {field} type: expect int or float', 401
            if not 0 <= data[field] <= 100:
                return f'ERROR: invalid {field} range', 401
            parameter[field] = data[field]
        elif field == 'strong_threshold' or field == 'weak_threshold' or field == 'medium_threshold':
            if not (isinstance(data[field], float) or isinstance(data[field], int)):
                return f'ERROR: invalid {field} type: expect int or float', 401
            if not 0 <= data[field] <= 1:
                return f'ERROR: invalid {field} range', 401
            parameter[field] = data[field]
        elif field == 'auto_threshold':
            if not isinstance(data[field], bool):
                return f'ERROR: invalid {field} type: expect boolean', 401
            parameter[field] = data[field]
        else:
            return 'ERROR: invalid field name', 401
    if sum(parameter['weight'].values()) != 1:
        return 'ERROR: weight summation is not equal 1', 401
    if not parameter['weak_threshold'] <= parameter['medium_threshold'] <= parameter['strong_threshold']:
        return 'ERROR: threshold must follow constraint: weak_threshold <= medium_threshold <= strong_threshold'
    Write.save_to_file(parameter, 'parameter.json')
    return 'success'


def reset_parameter():
    parameter = {'auto_threshold': True, 'data_range': 20, 'half_weight_frequency': 9, 'medium_threshold': 1.0,
                 'tail_percentile': 1, 'strong_threshold': 1.0, 'weak_threshold': 1.0, 'weight': {
                    "bathroom": 0.1,
                    "bedroom": 0.1,
                    "floor": 0.2,
                    "price": 0.35,
                    "size": 0.1,
                    "tower": 0.15
                 }}
    Write.save_to_file(parameter, 'parameter.json')
    return jsonify(parameter)


if __name__ == "__main__":
    test_post = '1234'
    result, result_2, result_3 = check_post(test_post)
