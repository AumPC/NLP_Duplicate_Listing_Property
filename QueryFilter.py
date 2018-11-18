import psycopg2
import psycopg2.extras
import json
import re


def query(query_command):
    # connect to postgresql database using psycopg2
    # in python3, do not pip psycopg2. please pip psycopg2-binary instead
    # tip: use RealDictCursor to query object as dictionary
    file_object = open('./password_db.txt', 'r')
    conn = psycopg2.connect("dbname=Temp user=postgres password="+file_object.readline())
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query_command)
    rows = cur.fetchall()
    print("The number of data: ", cur.rowcount)
    listing = []
    for row in rows:
        condo = {'id': row['id'], 'user_id': row['user_id'], 'title': row['title']}
        if 'max_rental_price' in row['price']['rental'] and row['price']['rental']['max_rental_price']:
            condo['price'] = [float(row['price']['rental']['min_rental_price']), float(row['price']['rental']['max_rental_price'])]
        elif row['price']['rental']['min_rental_price']:
            condo['price'] = [float(row['price']['rental']['min_rental_price']), None]
        else:
            condo['price'] = [0, None]
        condo['project'] = row['condo_project_id']
        condo['size'] = float(row['room_information']['room_area'])
        condo['tower'] = row['room_information']['building']
        if not condo['tower']:
            condo['tower'] = 'TEST'
        condo['floor'] = row['room_information']['on_floor']
        condo['type'] = row['room_information']['room_type']
        condo['bedroom'] = row['room_information']['no_of_bed']
        condo['bathroom'] = row['room_information']['no_of_bath']
        condo['detail'] = clear_tag(row['detail'])
        listing.append(condo)
    return listing


def read_json_file(filename):
    open_file = open(filename, 'r')
    data = json.load(open_file)
    return data


def clear_tag(detail):
    detail = re.sub('<.*?>|&nbsp;|&gt;|==|\*\*|---|\\\\|//', ' ', detail)
    # print (detail, '\n')
    return detail


def filter(rows):
    # compare every pair in rows. return pair which very possible to be duplicate
    # use price , size (in range) and project name
    group = {}
    for row in rows:
        if row['project'] not in group:
            group[row['project']] = [row]
        else:
            group[row['project']].append(row)
    return group
