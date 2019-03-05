import psycopg2
import psycopg2.extras
import json
import re
from string import ascii_letters, punctuation, digits, whitespace


def query(query_command, is_local, DEBUG):
    param_db = read_json_file('../parameter_db.json')
    conn = psycopg2.connect("dbname=" + param_db['db_name'] + "user=" + param_db['username'] + "password=" + param_db['password'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query_command)
    rows = cur.fetchall()
    if DEBUG:
        print("The number of data: ", cur.rowcount)
    listing = []
    if not is_local:
        for row in rows:
            condo = {'id': row['id'], 'user_id': row['user_id'], 'title': row['title']}
            if 'max_rental_price' in row['price']['rental'] and row['price']['rental']['max_rental_price']:
                condo['price'] = [float(row['price']['rental']['min_rental_price']), float(row['price']['rental']['max_rental_price'])]
            elif row['price']['rental']['min_rental_price']:
                condo['price'] = [float(row['price']['rental']['min_rental_price']), float(row['price']['rental']['min_rental_price'])]
            else:
                condo['price'] = None
            condo['project'] = row['condo_project_id']
            condo['size'] = float(row['room_information']['room_area'])
            condo['tower'] = row['room_information']['building']
            condo['floor'] = row['room_information']['on_floor']
            condo['bedroom'] = row['room_information']['no_of_bed']
            condo['bathroom'] = row['room_information']['no_of_bath']
            condo['detail'] = normalize_space(filter_special_character(clear_tag(row['detail'])))
            listing.append(condo)
    else:
        listing = rows
    return listing


def read_json_file(filename):
    open_file = open(filename, 'r')
    data = json.load(open_file)
    return data


def normalize_space(detail):
    detail = ' '.join(detail.split())
    return detail


def clear_tag(detail):
    detail = re.sub('<.*?>|&nbsp;|&gt;|&lt;|==|\*\*', ' ', detail)
    detail = re.sub('\t|=[=]+|:[:]+|/[/]+|\\[\\]+|-[-]+', '', detail)
    detail = re.sub('[ ]+', ' ', detail)
    detail = detail.split('\r\n')
    for index in range(len(detail)):
        detail[index] = re.sub('^[-\*#= ]+|[\*]$', '', detail[index])
    detail = '\r\n'.join(detail)
    return detail


def filter_special_character(detail):
    allowed = set(ascii_letters + digits + punctuation + whitespace)
    output = [char for char in detail if char in allowed or (ord(char) >= 3585 and ord(char) <= 3674)]
    detail = ''.join(output)
    return detail


def write_database(data):
    #TODO version 1 : replace data to local database
    pass
