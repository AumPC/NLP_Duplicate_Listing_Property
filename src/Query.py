import psycopg2
import psycopg2.extras
import json
import re
from string import ascii_letters, punctuation, digits, whitespace
import datetime

def query(query_command, is_local, DEBUG):
    param_db = read_json_file('parameter_db.json')
    conn = psycopg2.connect("dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query_command)
    rows = cur.fetchall()
    if DEBUG:
        print("The number of data: ", cur.rowcount)
    cur.close()
    conn.close()
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
        listing = rows # TODO Logic
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


def create_table(table_name, DEBUG):
    if DEBUG:
        print("Creating Table: ", table_name)
    command = {
        'extracted_table': """  
                CREATE TABLE public.condo_listings_extracted
                (
                    id integer NOT NULL ,
                    condo_project_id integer NOT NULL,
                    title character varying(255) NOT NULL,
                    price double precision [2] NOT NULL,
                    size double precision NOT NULL,
                    tower character varying(255) NOT NULL,
                    floor character varying(255) NOT NULL,
                    bedroom integer NOT NULL,
                    bathroom integer NOT NULL,
                    detail jsonb NOT NULL,
                    updated_at timestamp without time zone
                ) """,
        'compared_table': """ 
                CREATE TABLE public.condo_listings_compare_result
                (
                    id integer NOT NULL ,
                    strong_group character varying(255),
                    medium_group character varying(255),
                    weak_group character varying(255),
                    is_core character varying(255),
                    multiple_row boolean NOT NULL,
                    not_match boolean NOT NULL,
                    updated_at timestamp without time zone
                ) """
    }
    param_db = read_json_file('parameter_db.json')
    conn = psycopg2.connect("dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
    cur = conn.cursor()
    cur.execute(command[table_name])
    cur.close()
    conn.commit()
    if conn is not None:
        conn.close()


def write_database(table_name, data, DEBUG):
    data = {'id': 392858, 'user_id': 107118, 'title': 'ให้เช่า : UNiO Sukhumvit 72 ใกล้ BTS แบริ่ง 1ห้องนอน ห้องใหม่ ทิศเหนือ วิวสระว่ายน้ำ!!!', 'price': [10000.0, 10000.0], 
            'project': 2764, 'size': 27.0, 'tower': '', 'floor': '3', 'bedroom': '1', 'bathroom': '1', 
            'detail': json.dumps({})}
    data['date'] = datetime.datetime.now()
    if DEBUG:
        print("Writing Table: ", table_name)
    command = {
        'extracted_table': """  
                INSERT INTO public.condo_listings_extracted (id, condo_project_id, title, price, size, tower, floor, bedroom, bathroom, detail, updated_at)
                VALUES (%(id)s, %(project)s, %(title)s, %(price)s, %(size)s, %(tower)s, %(floor)s, %(bedroom)s, %(bathroom)s, %(detail)s, %(date)s);
        """,
        'compared_table': """ 
                INSERT INTO public.condo_listings_compare_result (an_int, a_date, another_date, a_string)
                VALUES (%(int)s, %(date)s, %(date)s, %(str)s);
        """
    }
    param_db = read_json_file('parameter_db.json')
    conn = psycopg2.connect("dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
    cur = conn.cursor()
    cur.execute(command[table_name], data)
    cur.close()
    conn.commit()
    if conn is not None:
        conn.close()