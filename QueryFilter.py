import psycopg2
import psycopg2.extras

import re

def query():
    # connect to postgresql database using psycopg2
    # in python3, do not pip psycopg2. please pip psycopg2-binary instead
    # tip: use RealDictCursor to query object as dictionary
    conn = psycopg2.connect("dbname=Temp user=postgres password=")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM condo_listings_sample order by condo_project_id, user_id DESC limit 100")
    rows = cur.fetchall()
    print("The number of data: ", cur.rowcount)
    listing = []
    for row in rows:
        condo = {}
        condo['id'] = row['id']
        condo['user_id'] = row['user_id']
        condo['title'] = row['title']
        if 'max_rental_price' in row['price']['rental'] and row['price']['rental']['max_rental_price']:
            condo['price'] = [float(row['price']['rental']['min_rental_price']), float(row['price']['rental']['max_rental_price'])]
        elif row['price']['rental']['min_rental_price']:
            condo['price'] = [float(row['price']['rental']['min_rental_price']), None]
        else:
            condo['price'] = [0 , None]
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

def clear_tag(detail):
    detail = re.sub('<.*?>|&nbsp;|&gt;|==|\*\*|---|\\\\|\/\/', ' ', detail)
    # print (detail, '\n')
    return detail


def filter(rows):
    # compare every pair in rows. return pair which very possible to be duplicate
    # use price , size (in range) and project name
    summary = []
    project_id = rows[0]['project']
    group = []
    for row in rows:
        if row['project'] != project_id:
            summary.append(group)
            project_id = row['project']
            group = []
        group.append(row)
    summary.append(group)
    return summary
