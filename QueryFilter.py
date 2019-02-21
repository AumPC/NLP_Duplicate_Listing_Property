import psycopg2
import psycopg2.extras
import json
import re
from operator import itemgetter
from itertools import groupby
from string import ascii_letters, punctuation, digits, whitespace


def query(query_command):
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

def filter(rows):
    # compare every pair in rows. return pair which very possible to be duplicate
    # use price , size (in range) and project name
    group = {k: list(v) for k, v in groupby(rows, key=itemgetter('project'))}
    return {k: v for k, v in group.items() if len(v) > 1}
