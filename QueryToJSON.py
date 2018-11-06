import QueryFilter as QF
import json

# export from database to JSON

def save_to_file(data, filename):
    open_file = open(filename, 'w')
    json.dump(data, open_file, sort_keys=True, indent=4)

if __name__ == "__main__":
    # query here
    query_command = "SELECT * FROM condo_listings_sample where id != 576432 order by condo_project_id, user_id DESC limit 100"
    # file path here
    file_path = "src/condo_listings_sample.json"
    data = QF.query(query_command)
    save_to_file(data, file_path)