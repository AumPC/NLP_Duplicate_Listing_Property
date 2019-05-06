import re
import string
from operator import itemgetter
from itertools import groupby


def extraction_price_before(detail, keyword):
    ext_price_arr = []
    for key in keyword:
        for price in detail.split(key)[:-1]:
            point = len(price) - 1
            while price[point] in '0123456789, ':
                point -= 1
                if point < 0:
                    break
            ext_price_arr.append(price[point + 1:])
    return ext_price_arr


def extraction_price_after(detail, keyword):
    ext_price_arr = []
    for key in keyword:
        for price in detail.split(key)[1:]:
            point = 0
            if len(price) == 0:
                continue
            while price[point] in '0123456789, ':
                point += 1
                if point >= len(price):
                    break
            ext_price_arr.append(price[0:point])
    return ext_price_arr


def extraction_price(detail):
    prefix_keyword = ['บาท', 'baht']
    postfix_keyword = ['ราคา']
    ext_price = extraction_price_before(detail, prefix_keyword) + extraction_price_after(detail, postfix_keyword)
    ext_price = [re.sub('[, ]', '', price) for price in ext_price]
    ext_price = [float(price) for price in ext_price if price and 1000 < float(price) < 1000000]
    ext_price = sorted(list(set(ext_price)))
    if len(ext_price) > 2:
        return -1
    if not ext_price:
        return None
    return [ext_price[0], ext_price[-1]]


def extraction_size_before(detail, keyword):
    ext_size_arr = []
    for key in keyword:
        for size in detail.split(key)[:-1]:
            point = len(size) - 1
            while size[point] in '0123456789 /,.-':
                point -= 1
                if point < 0:
                    break
            found = size[point + 1:]
            have_floor = size.split('ชั้น')
            if len(have_floor) > 1 and have_floor[-1] == found:
                found = [value for value in re.split('[ /,]', found) if value]
                if len(found) > 1:
                    found = found[1:]
                found = ' '.join(found)
            ext_size_arr.append(found)
    return ext_size_arr


def extraction_size_after(detail, keyword):
    ext_size_arr = []
    for key in keyword:
        for size in detail.split(key)[1:]:
            point = 0
            if size == '':
                continue
            while size[point] in '0123456789 /,.-':
                point += 1
                if point >= len(size):
                    break
            ext_size_arr.append(size[0:point])
    return ext_size_arr


def extraction_size(detail):
    prefix_keyword = [
        'ตรม', 'ตร.ม', 'ตร ม', 'ตร. ม', 'ตารางเมตร', 'ตารางวา', 'ตาราง.ม.',
        'Square meters', 'Square meters',
        'SQ.M', 'SQ.m', 'Sq.M', 'Sq.m', 'sQ.M', 'sQ.m', 'sq.M', 'sq.m',
        'SQM ', 'SQm ', 'SqM ', 'Sqm ', 'sQM ', 'sQm ', 'sqM ', 'sqm ',
        'SQM.', 'SQm.', 'SqM.', 'Sqm.', 'sQM.', 'sQm.', 'sqM.', 'sqm.',
        'sqm,'
    ]
    postfix_keyword = [
        # 'ขนาด', 'พื้นที่',
        'sq.m.):']
    ext_size_arr = extraction_size_before(detail, prefix_keyword) + extraction_size_after(detail, postfix_keyword)
    ext_size = []
    for size in ext_size_arr:
        temp_arr = []
        split_value = re.split('[ /,-]', size)
        for value in split_value:
            if not value or value[0] == '.' or value[-1] == '.':
                continue
            if (len(value) == 3 and value[0] in '0123456789' and value[1] in '0' and value[2] in '0') or (
                    float(value) < 10):
                if temp_arr:
                    temp_arr.pop()
                continue
            if 19 < float(value) < 1000:
                temp_arr.append(float(value))
        ext_size += temp_arr
    ext_size = list(set(ext_size))
    if len(ext_size) > 1:
        return -1
    if not ext_size:
        return None
    return ext_size[0]


def extraction_tower(detail):
    thai_building = {'เอ': 'A', 'บี': 'B', 'ซี': 'C', 'ดี': 'D', 'อี': 'E', 'เอฟ': 'F', 'จี': 'G'}
    number_building = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    combined_building = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
                         'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
                         'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                         'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
                         'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9',
                         'CENTER', 'WEST', 'EAST']
    name_building = set(list(thai_building.keys()) + number_building + list(string.ascii_letters) + combined_building)
    keyword = ['ตึก', 'อาคาร']
    ext_tower_arr = []
    for key in keyword:
        for tower in detail.split(key)[1:]:
            point = 0
            if tower == '':
                continue
            found = 0
            while point < len(tower) and (tower[point] not in ' \r\n(' or found != 2):
                if tower[point] in '0123456789' and found <= 1:
                    found = 1
                elif tower[point] not in '\r\n ':
                    found = 2
                point += 1
            ext_tower = tower[0:point]
            if 'ตึก' in ext_tower or 'อาคาร' in ext_tower or 'คัน' in ext_tower or 'ตัว' in ext_tower or\
                    'ทาวเวอร์' in ext_tower:
                continue
            if 'ชั้น' in ext_tower:
                is_floor = tower.split('ชั้น')[1]
                point = 0
                while point < len(is_floor) and is_floor[point] not in ' ':
                    point += 1
                if point == len(is_floor) or is_floor[point] not in '0123456789':
                    continue
            ext_tower_arr += re.split('[ /,]', ext_tower)
    ext_tower_arr = list(set(ext_tower for ext_tower in ext_tower_arr if ext_tower in name_building))
    for i in range(len(ext_tower_arr)):
        if ext_tower_arr[i] in thai_building.keys():
            ext_tower_arr[i] = thai_building[ext_tower_arr[i]]
        else:
            ext_tower_arr[i] = ext_tower_arr[i].upper()
    ext_tower_arr = list(set(ext_tower_arr))
    if len(ext_tower_arr) > 1:
        return -1
    if not ext_tower_arr:
        return None
    return ext_tower_arr[0]


def extraction_bed_bath(detail):
    patterns = ['([0-9, ]+)ห้องนอน([0-9, ]+)ห้องน้ำ', '([0-9, ]+)นอน([0-9, ]+)น้ำ',
                '([0-9, ]+)bedroom([0-9, ]+)bathroom', '([0-9, ]+)bed([0-9, ]+)bath']
    bedroom = set()
    bathroom = set()
    for p in patterns:
        exp = re.compile(p)
        for i in exp.findall(detail):
            bed = [j for j in re.split(' ', re.sub(',', '', i[0])) if j != '']
            bed = [bed[-1]] if len(bed) > 0 else None
            bath = [j for j in re.split(' ', re.sub(',', '', i[1])) if j != '']
            bath = [bath[-1]] if len(bath) > 0 else None
            if bed is not None and bath is not None:
                bedroom.update(bed)
                bathroom.update(bath)
    if not bedroom and not bathroom:
        patterns = ['ห้องนอน([0-9, ]+)ห้องน้ำ([0-9, ]+)', 'นอน([0-9, ]+)น้ำ([0-9, ]+)',
                    'bedroom([0-9, ]+)bathroom([0-9, ]+)', 'bed([0-9, ]+)bath([0-9, ]+)'
                    ]
        for p in patterns:
            exp = re.compile(p)
            for i in exp.findall(detail):
                bed = [j for j in re.split(' ', re.sub(',', '', i[0])) if j != '']
                bed = [bed[0]] if len(bed) > 0 else None
                bath = [j for j in re.split(' ', re.sub(',', '', i[1])) if j != '']
                bath = [bath[0]] if len(bath) > 0 else None
                if bed is not None and bath is not None:
                    bedroom.update(bed)
                    bathroom.update(bath)
    if len(bedroom) > 1 or len(bathroom) > 1:
        return -1, -1
    bedroom = bedroom.pop() if len(bedroom) > 0 else None
    bathroom = bathroom.pop() if len(bathroom) > 0 else None
    return bedroom, bathroom


def check_leftover(text):
    cut_text = ['ห้องนอน', 'ตร', 'ตาราง']
    for cut in cut_text:
        leftover = text.split(cut)
        if len(leftover) > 1 and leftover[0] == '':
            return True
    return False


def extraction_floor_before(floor, ext_floor):
    if ext_floor == -1:
        return -1
    for i in range(len(floor) - 1):
        point = 0
        if floor[i + 1] == '':
            continue
        while floor[i + 1][point] in ' 0123456789' + string.ascii_letters:
            point += 1
            if point >= len(floor[i + 1]):
                break
        ext_floor_arr = [floor for floor in re.split('[ /,]', floor[i + 1][0:point].upper()) if floor]
        if ext_floor_arr and check_leftover(floor[i + 1][point:]):
            ext_floor_arr.pop()
        for value in ext_floor_arr:
            try:
                if int(value) > 40:
                    continue
            except ValueError:
                if value == '12A':
                    pass
                else:
                    continue
            if ext_floor is None:
                ext_floor = value
            if ext_floor != value:
                return -1
    return ext_floor


def extraction_floor(detail):
    ext_floor = None
    all_floor = detail.split('จำนวนชั้น')
    length = len(all_floor)
    if length == 1:
        floor = detail.split('ชั้น')
        ext_floor = extraction_floor_before(floor, ext_floor)
    else:
        for f in all_floor[1:length - 1]:
            floor = f.split('ชั้น')
            ext_floor = extraction_floor_before(floor, ext_floor)
    return ext_floor


def detail_extraction(detail):
    ext = {'price': None, 'size': None, 'tower': None, 'floor': None, 'bedroom': None, 'bathroom': None}
    if not detail:
        return ext
    ext['price'] = extraction_price(detail)
    ext['size'] = extraction_size(detail)
    ext['tower'] = extraction_tower(detail)
    ext['bedroom'], ext['bathroom'] = extraction_bed_bath(detail)
    ext['floor'] = extraction_floor(detail)
    if ext['price'] == -1 or ext['size'] == -1 or ext['tower'] == -1 or ext['bedroom'] == -1 or ext['bathroom'] == -1:
        return -1
    return ext


def extraction(rows, debug):
    filter_rows = []
    multiple_row = []
    check_floor_row = []
    not_match_row = []
    not_found = {'price': 0, 'size': 0, 'tower': 0, 'bedroom': 0, 'bathroom': 0, 'floor': 0}
    for row in rows:
        ext = detail_extraction(row['detail'])
        if ext == -1:
            multiple_row.append(row['id'])
            continue
        if ext['price'] is None:
            not_found['price'] += 1
        if ext['size'] is None:
            not_found['size'] += 1
        if ext['tower'] is None:
            not_found['tower'] += 1
        if ext['bedroom'] is None:
            not_found['bedroom'] += 1
        if ext['bathroom'] is None:
            not_found['bathroom'] += 1
        if ext['floor'] is None:
            not_found['floor'] += 1
        if ext['price'] is not None:
            if row['price'] is None:
                row['price'] = ext['price']
            elif (row['price'][0] == row['price'][1] and (
                    ext['price'][0] != row['price'][0] and ext['price'][1] != row['price'][0])) or \
                    (row['price'][0] != row['price'][1] and ext['price'] != row['price']):
                not_match_row.append(row['id'])
                continue
        if ext['size'] is not None and ext['size'] != row['size']:
            if row['size'] == '' or row['size'] is None:
                row['size'] = ext['size']
            else:
                not_match_row.append(row['id'])
                continue
        if ext['tower'] is not None and ext['tower'] != row['tower']:
            if row['tower'] == '' or row['tower'] is None:
                row['tower'] = ext['tower']
            else:
                not_match_row.append(row['id'])
                continue
        if ext['bedroom'] is not None and ext['bedroom'] != row['bedroom']:
            if row['bedroom'] == '' or row['bedroom'] is None:
                row['bedroom'] = ext['bedroom']
            else:
                not_match_row.append(row['id'])
                continue
        if ext['bathroom'] is not None and ext['bathroom'] != row['bathroom']:
            if row['bathroom'] == '' or row['bathroom'] is None:
                row['bathroom'] = ext['bathroom']
            else:
                not_match_row.append(row['id'])
                continue
        if ext['floor'] is not None and ext['floor'] != row['floor']:
            if row['floor'] == '' or row['floor'] is None:
                row['floor'] = ext['floor']
            elif ext['floor'] == -1:
                check_floor_row.append(row['id'])
                ext['floor'] = None
                not_found['floor'] += 1
            else:
                not_match_row.append(row['id'])
                continue
        row['ext'] = ext
        filter_rows.append(row)
    if debug:
        print("Not Found Context", not_found)
        print("Multiple Context", len(multiple_row), 'items')
        print("Floor Multiple Context", len(check_floor_row), 'items')
        print("Not Match Context", len(not_match_row), 'items')
    return filter_rows, multiple_row, not_match_row


def group_by_project(rows):
    group = {k: list(v) for k, v in groupby(rows, key=itemgetter('project'))}
    return {k: v for k, v in group.items() if len(v) > 1}
