import Query as Q
import ExtractionFilter as Extr
import Similarity as Sim
import WriteFile as W


QUERY = False
DEBUG = True


if __name__ == "__main__":
    if DEBUG:
        print("-- Query --")
    parameter = Q.read_json_file("parameter.json")
    if QUERY:
        query_command = "SELECT * FROM condo_listings_sample where id != 576432 order by condo_project_id, user_id DESC"
        rows = Q.query(query_command, DEBUG)
    else:
        rows = Q.read_json_file("./src/condo_listings_dup.json")
    if DEBUG:
        print("-- Extraction & Filter --")
    filter_rows, multiple_row, check_floor_row, not_match_row, not_found = Extr.extraction(rows)
    if DEBUG:
        print("Not Found Context", not_found)
        print("Multiple Context", len(multiple_row), 'items')
        print("Floor Multiple Context", len(check_floor_row), 'items', check_floor_row)
        print("Not Match Context", len(not_match_row), 'items')
    projects = Extr.group_by_project(filter_rows)
    group_word_matrix = Sim.tokenize(projects, DEBUG)
    if DEBUG:
        print("-- Scoring --")
    strong_duplicate, medium_duplicate, weak_duplicate = Sim.similarity(projects, group_word_matrix, parameter)
    if DEBUG:
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
    results = W.construct_data_frame(rows)
    results = W.cal_results(results, strong_duplicate, medium_duplicate, weak_duplicate)
    W.write_results_pickle(results)
    W.write_results_csv(results)
