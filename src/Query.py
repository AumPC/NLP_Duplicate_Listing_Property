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
        condo['tower'] = process_tower(row['room_information']['building'])

        condo['floor'] = process_floor(row['room_information']['on_floor'])
        condo['bedroom'] = process_bed_bath(row['room_information']['no_of_bed'])
        condo['bathroom'] = process_bed_bath(row['room_information']['no_of_bath'])
        condo['detail'] = process_detail(row['detail'])
        listing.append(condo)
    return listing


def read_json_file(filename):
    open_file = open(filename, 'r')
    data = json.load(open_file)
    return data

def clean_replace_text(text, cut_name, replace_arr):
    for i in cut_name:
        text = text.split(i)[-1]
    text = re.sub(' ', '', text)
    start = 0
    thai_vowels = ['ฤ', 'ฦ', 'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู',  '็', '่', 'ฺ',  '์', ',']
    while start < len(text) and text[start] in thai_vowels:
        start += 1
    text = text[start:].upper()
    for i in replace_arr.keys():
        text = re.sub(i, replace_arr[i], text)
    return text


def process_bed_bath(bed_bath):
    if bed_bath is None or bed_bath == '' or bed_bath == '-':
        return bed_bath
    bed_bath_name = ['ห้องนอน', 'นอน', 'bed', 'bedroom', 'ห้องน้ำ', 'น้ำ', 'bath', 'bathroom']
    bed_bath_replace = {'STUDIO': '1', 'STUDIOS': '1'}
    bed_bath = clean_replace_text(bed_bath, bed_bath_name, bed_bath_replace)
    return bed_bath


def process_tower(tower):
    if tower is None or tower == '' or tower == '-':
        return tower
    build_name = ['อาคาร', 'ตึก', 'building', 'BUILDING', 'Building', 'tower', 'Tower', 'TOWER']
    thai_building = {'เอ': 'A', 'บี': 'B', 'ซี': 'C', 'ดี': 'D', 'อี': 'E', 'เอฟ': 'F', 'จี': 'G'}
    tower = clean_replace_text(tower, build_name, thai_building)
    return tower


def process_floor(floor):
    if floor is None or floor == '' or floor == '-':
        return floor
    floor_name = ['ชั้น', 'floor']
    thai_building = {'เอ': 'A', 'บี': 'B', 'ซี': 'C', 'ดี': 'D', 'อี': 'E', 'เอฟ': 'F', 'จี': 'G'}
    floor = clean_replace_text(floor, floor_name, thai_building)    
    return floor


def process_detail(detail):
    return normalize_space(filter_special_character(clear_tag(detail)))


def normalize_space(detail):
    detail = ' '.join(detail.split())
    return detail


def clear_tag(detail):
    detail = re.sub(r'<.*?>|&nbsp;|&gt;|&lt;|==|\*\*', ' ', detail)
    detail = re.sub('\t|=[=]+|:[:]+|/[/]+|\\[\\]+|-[-]+', '', detail)
    detail = re.sub('[ ]+', ' ', detail)
    detail = '\r\n'.join([re.sub('^[-*#= ]+|[*]$', '',text) for text in detail.split('\r\n')])
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
                    project integer,
                    title character varying(255) NOT NULL,
                    price double precision [2],
                    size double precision NOT NULL,
                    tower character varying(255) NOT NULL,
                    floor character varying(255) NOT NULL,
                    bedroom character varying(255) NOT NULL,
                    bathroom character varying(255) NOT NULL,
                    detail integer [] NOT NULL,
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
                INSERT INTO public.projects (id, project, title, price, size, tower, floor, bedroom, bathroom, detail, ext)
                VALUES (%(id)s, %(project)s, %(title)s, %(price)s, %(size)s, %(tower)s, %(floor)s, %(bedroom)s, %(bathroom)s, %(detail)s, %(ext)s)
                ON CONFLICT (id) DO UPDATE SET (project, title, price, size, tower, floor, bedroom, bathroom, detail, ext) = 
                (EXCLUDED.project, EXCLUDED.title, EXCLUDED.price, EXCLUDED.size, EXCLUDED.tower, 
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
        if isinstance(data, list):
            for row in data:
                row['detail'] = row['detail'].astype(int).tolist()
                row['ext'] = json.dumps(row['ext'])
            psycopg2.extras.execute_batch(cur, command[table_name], data)
        else:
            for project in data.values():
                for condo in project:
                    condo['detail'] = condo['detail'].astype(int).tolist()
                    condo['ext'] = json.dumps(condo['ext'])
                psycopg2.extras.execute_batch(cur, command[table_name], project)
    if table_name == 'corpus':
        psycopg2.extras.execute_batch(cur, command[table_name], data)
    cur.close()
    conn.commit()
    conn.close()
