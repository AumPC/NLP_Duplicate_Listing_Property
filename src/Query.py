import psycopg2
import psycopg2.extras
import json
import re
from string import ascii_letters, punctuation, digits, whitespace
import datetime


def query(query_command, is_local, DEBUG):
    if is_local:
        param_db = read_json_file('parameter_db.json')
        conn = psycopg2.connect(
            "dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query_command)
        rows = cur.fetchall()
        if DEBUG:
            print("The number of data: ", cur.rowcount)
        return rows
    param_db = read_json_file('parameter_db.json')  # TODO global db param
    conn = psycopg2.connect(
        "dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
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
                condo['price'] = [float(row['price']['rental']['min_rental_price']),
                                  float(row['price']['rental']['max_rental_price'])]
            elif row['price']['rental']['min_rental_price']:
                condo['price'] = [float(row['price']['rental']['min_rental_price']),
                                  float(row['price']['rental']['min_rental_price'])]
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
            # print(condo)
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
        detail[index] = re.sub('^[-*#= ]+|[*]$', '', detail[index])
    detail = '\r\n'.join(detail)
    return detail


def filter_special_character(detail):
    allowed = set(ascii_letters + digits + punctuation + whitespace)
    output = [char for char in detail if char in allowed or (3585 <= ord(char) <= 3674)]
    detail = ''.join(output)
    return detail


def create_table(table_name, conn, cur, DEBUG):
    if DEBUG:
        print("Creating Table: ", table_name)
    command = {
        'projects': """  
                CREATE TABLE public.projects
                (
                    id integer NOT NULL ,
                    condo_project_id integer NOT NULL,
                    user_id integer NOT NULL,
                    title character varying(255) NOT NULL,
                    price double precision [2] NOT NULL,
                    size double precision NOT NULL,
                    tower character varying(255) NOT NULL,
                    floor character varying(255) NOT NULL,
                    bedroom integer NOT NULL,
                    bathroom integer NOT NULL,
                    detail float [] NOT NULL,
                    ext jsonb NOT NULL,
                    updated_at timestamp without time zone default current_timestamp,
                    CONSTRAINT projects_pkey PRIMARY KEY (id)
                ) """,
        'corpus': """ 
                CREATE TABLE public.corpus
                (
                    condo_project_id integer NOT NULL ,
                    corpus text [],
                    CONSTRAINT corpus_pkey PRIMARY KEY (condo_project_id)
                ) """
    }
    cur.execute(command[table_name])
    conn.commit()


def write_database(table_name, data, DEBUG):  # TODO upsert
    # data = {'id': 392858, 'user_id': 107118,
    #         'title': 'ให้เช่า : UNiO Sukhumvit 72 ใกล้ BTS แบริ่ง 1ห้องนอน ห้องใหม่ ทิศเหนือ วิวสระว่ายน้ำ!!!',
    #         'price': [10000.0, 10000.0], 'project': 2764, 'size': 27.0, 'tower': '', 'floor': '3', 'bedroom': '1',
    #         'bathroom': '1', 'detail': json.dumps({}), 'date': datetime.datetime.now()}
    check_command = f"SELECT EXISTS ( SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' and table_name = '{ table_name }');"
    command = {
        'projects': """  
                INSERT INTO public.projects (id, user_id, condo_project_id, title, price, size, tower, floor, bedroom, bathroom, detail, ext)
                VALUES (%(id)s, %(user_id)s, %(project)s, %(title)s, %(price)s, %(size)s, %(tower)s, %(floor)s, %(bedroom)s, %(bathroom)s, %(detail)s, %(ext)s)
                ON CONFLICT (id) DO UPDATE SET (user_id, condo_project_id, title, price, size, tower, floor, bedroom, bathroom, detail, ext) = 
                (EXCLUDED.user_id, EXCLUDED.condo_project_id, EXCLUDED.title, EXCLUDED.price, EXCLUDED.size, EXCLUDED.tower, 
                EXCLUDED.floor, EXCLUDED.bedroom, EXCLUDED.bathroom, EXCLUDED.detail, EXCLUDED.ext);
        """,
        'corpus': """ 
                INSERT INTO public.corpus (condo_project_id, corpus)
                VALUES (%(condo_project_id)s, %(corpus)s) 
                ON CONFLICT (condo_project_id) DO UPDATE SET corpus = EXCLUDED.corpus;
        """
    }
    param_db = read_json_file('parameter_db.json')
    if DEBUG:
        print("Writing : ", table_name)
    conn = psycopg2.connect(
        "dbname=" + param_db['db_name'] + " user=" + param_db['username'] + " password=" + param_db['password'])
    cur = conn.cursor()
    cur.execute(check_command)
    if not cur.fetchall()[0][0]:
        create_table(table_name, conn, cur, DEBUG)
    if table_name == 'projects':
        for project in data.values():
            for condo in project:
                condo['detail'] = condo['detail'].astype(float).tolist()
                condo['ext'] = json.dumps(condo['ext'])
                cur.execute(command[table_name], condo)
            # cur.executemany(command[table_name], condo)
    if table_name == 'corpus':
        cur.execute(command[table_name], data)
    cur.close()
    conn.commit()
    conn.close()
