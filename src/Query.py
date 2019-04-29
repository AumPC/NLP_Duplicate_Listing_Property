import psycopg2
import psycopg2.extras
import json
import re
from string import ascii_letters, punctuation, digits, whitespace


def query(query_command, is_local, debug):
    if is_local:
        param_db = read_json_file('parameter_nlp_db.json')
        conn = psycopg2.connect(f"dbname={param_db['db_name']} user= {param_db['username']} password= {param_db['password']}")
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query_command)
        rows = cur.fetchall()
        if debug:
            print("The number of data: ", cur.rowcount)
        return rows
    param_db = read_json_file('parameter_main_db.json')
    conn = psycopg2.connect(f"dbname={param_db['db_name']} user= {param_db['username']} password= {param_db['password']}")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query_command)
    rows = cur.fetchall()
    if debug:
        print("The number of data: ", cur.rowcount)
    cur.close()
    conn.close()
    listing = []
    for row in rows:
        condo = {'id': row['id'], 'title': row['title']}
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
    return listing


def read_json_file(filename):
    open_file = open(filename, 'r')
    data = json.load(open_file)
    return data


def normalize_space(detail):
    detail = ' '.join(detail.split())
    return detail


def clear_tag(detail):
    detail = re.sub(r'<.*?>|&nbsp;|&gt;|&lt;|==|\*\*', ' ', detail)
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


def create_table(table_name, conn, cur, debug):
    if debug:
        print("Creating Table :", table_name)
    command = {
        'projects': """  
                CREATE TABLE public.projects
                (
                    id integer NOT NULL ,
                    condo_project_id integer,
                    title character varying(255) NOT NULL,
                    price double precision [2],
                    size character varying(255) NOT NULL,
                    tower character varying(255) NOT NULL,
                    floor character varying(255) NOT NULL,
                    bedroom character varying(255) NOT NULL,
                    bathroom character varying(255) NOT NULL,
                    detail float [] NOT NULL,
                    ext jsonb NOT NULL,
                    updated_at timestamp without time zone default current_timestamp,
                    CONSTRAINT projects_pkey PRIMARY KEY (id)
                ) """,
        'corpus': """ 
                CREATE TABLE public.corpus
                (
                    id integer NOT NULL,
                    project integer,
                    corpus text [],
                    CONSTRAINT corpus_pkey PRIMARY KEY (id)
                ) """
    }
    cur.execute(command[table_name])
    conn.commit()


def write_database(table_name, data, debug):
    check_command = f"SELECT EXISTS ( SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' and table_name = '{ table_name }');"
    command = {
        'projects': """  
                INSERT INTO public.projects (id, condo_project_id, title, price, size, tower, floor, bedroom, bathroom, detail, ext)
                VALUES (%(id)s, %(project)s, %(title)s, %(price)s, %(size)s, %(tower)s, %(floor)s, %(bedroom)s, %(bathroom)s, %(detail)s, %(ext)s)
                ON CONFLICT (id) DO UPDATE SET (condo_project_id, title, price, size, tower, floor, bedroom, bathroom, detail, ext) = 
                (EXCLUDED.condo_project_id, EXCLUDED.title, EXCLUDED.price, EXCLUDED.size, EXCLUDED.tower, 
                EXCLUDED.floor, EXCLUDED.bedroom, EXCLUDED.bathroom, EXCLUDED.detail, EXCLUDED.ext);
        """,
        'corpus': """ 
                INSERT INTO public.corpus (id, project, corpus)
                VALUES (%(id)s, %(project)s, %(corpus)s) 
                ON CONFLICT (id) DO UPDATE SET (project, corpus) = (EXCLUDED.project, EXCLUDED.corpus);
        """
    }
    param_db = read_json_file('parameter_nlp_db.json')
    if debug:
        print("Writing :", table_name)
    conn = psycopg2.connect(f"dbname={param_db['db_name']} user= {param_db['username']} password= {param_db['password']}")
    cur = conn.cursor()
    cur.execute(check_command)
    if not cur.fetchall()[0][0]:
        create_table(table_name, conn, cur, debug)
    if table_name == 'projects':
        for project in data.values():
            for condo in project:
                condo['detail'] = condo['detail'].astype(float).tolist()
                condo['ext'] = json.dumps(condo['ext'])
            psycopg2.extras.execute_batch(cur, command[table_name], project)
    if table_name == 'corpus':
        psycopg2.extras.execute_batch(cur, command[table_name], data)
    cur.close()
    conn.commit()
    conn.close()
