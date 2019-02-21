import re
import string


def extraction_price_before(detail, keyword):
    ext_price_arr = []
    for key in keyword:
        price = detail.split(key)
        for i in range(len(price)-1):
            point = len(price[i])-1
            while price[i][point] in ' ,':
                point -= 1
                if point < 1:
                    break
            while price[i][point] in '0123456789,':
                point -= 1
                if point < 0:
                    break
            ext_str = re.sub('[, ]', '', price[i][point+1:])
            value = float(ext_str) if ext_str != "" else None
            if not value or not (1000 < value < 1000000):
                continue
            ext_price_arr.append(float(value))
    return ext_price_arr


def extraction_price_after(detail, keyword):
    ext_price_arr = []
    for key in keyword:
        price = detail.split(key)
        for i in range(len(price)-1):
            point = 0
            if len(price[i+1]) == 0:
                continue
            while price[i+1][point] in ' ,':
                point += 1
                if point >= len(price[i+1]):
                    break
            while point < len(price[i+1]) and price[i+1][point] in '0123456789,':
                point += 1
                if point >= len(price[i+1]):
                    break
            ext_str = re.sub('[, ]', '', price[i+1][0:point])
            value = float(ext_str) if ext_str != "" else None
            if not value or not (1000 < value < 1000000):
                continue
            ext_price_arr.append(float(value))
    return ext_price_arr


def extraction_price(detail):
    prefix_keyword = ['บาท', 'baht']
    postfix_keyword = ['ราคา']
    ext_price = list(set(extraction_price_before(detail, prefix_keyword) + extraction_price_after(detail, postfix_keyword)))
    if len(ext_price) > 2:
        return -1
    if not ext_price:
        return None
    return [ext_price[0], ext_price[-1]]


def extraction_size_before(detail, keyword):
    ext_size_arr = []
    for key in keyword:
        size = detail.split(key)
        for i in range(len(size)-1):
            point = len(size[i])-1
            while size[i][point] in '0123456789 /,.':
                point -= 1
                if point < 0:
                    break
            ext_size_arr += re.split('[ /,]', size[i][point+1:])
    ext_size_arr = [float(ext_size) for ext_size in ext_size_arr if ext_size and ext_size[0] != '.' and ext_size[-1] != '.' ]
    return ext_size_arr


def extraction_size_after(detail, keyword):
    ext_size_arr = []
    for key in keyword:
        size = detail.split(key)
        for i in range(len(size)-1):
            point = 0
            if size[i+1] == '':
                continue
            while size[i+1][point] in '0123456789 /,.':
                point += 1
                if point >= len(size[i+1]):
                    break
            ext_size_arr += re.split('[ /,]', size[i+1][0:point])
    ext_size_arr = [float(ext_size) for ext_size in ext_size_arr if ext_size and ext_size[0] != '.' and ext_size[-1] != '.' ]
    return ext_size_arr


def extraction_size(detail):
    prefix_keyword = [
        'ตรม', 'ตร.ม', 'ตร ม', 'ตร. ม',
        'ตารางเมตร', 'ตารางวา', 'ตาราง.ม.',
        'Square meters', 'Square meters',
        'SQ.M', 'SQ.m', 'Sq.M', 'Sq.m', 'sQ.M', 'sQ.m', 'sq.M', 'sq.m',
        'SQM ', 'SQm ', 'SqM ', 'Sqm ', 'sQM ', 'sQm ', 'sqM ', 'sqm ',
        'SQM.', 'SQm.', 'SqM.', 'Sqm.', 'sQM.', 'sQm.', 'sqM.', 'sqm.',
        'sqm,'
    ]
    postfix_keyword = [
        # 'ขนาด',
        # 'พื้นที่',
        'sq.m.):']
    ext_size = list(set(extraction_size_before(detail, prefix_keyword) + extraction_size_after(detail, postfix_keyword)))
    if len(ext_size) > 1:
        return -1
    if not ext_size:
        return None
    return ext_size[0]


def extraction_tower(detail):
    thai_building = ['เอ', 'บี', 'ซี', 'ดี', 'อี', 'เอฟ', 'จี']
    number_building = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    name_building = set(thai_building + number_building + list(string.ascii_letters))
    keyword = ['ตึก', 'อาคาร']
    ext_tower_arr = []
    for key in keyword:
        tower = detail.split(key)
        for i in range(len(tower) - 1):
            point = 0
            if tower[i + 1] == '':
                continue
            found = 0
            while point < len(tower[i + 1]) and (tower[i + 1][point] not in ' \r\n' or found != 2):
                if tower[i + 1][point] in '0123456789' and found <= 1:
                    found = 1
                elif tower[i + 1][point] not in '\r\n ':
                    found = 2
                point += 1
            ext_tower = tower[i + 1][0:point]
            if 'ตึก' in ext_tower or 'อาคาร' in ext_tower or 'คัน' in ext_tower or 'ชั้น' in ext_tower:
                continue
            ext_tower_arr += re.split('[ /,]', ext_tower)
    ext_tower_arr = list(set(ext_tower for ext_tower in ext_tower_arr if ext_tower in name_building))
    if len(ext_tower_arr) > 1:
        return -1
    if not ext_tower_arr:
        return None
    return ext_tower_arr[0]


def extraction_bed_bath(detail):
    patterns = ['([0-9, ]+)ห้องนอน([0-9, ]+)ห้องน้ำ', 'ห้องนอน([0-9, ]+)ห้องน้ำ([0-9, ]+)',
<<<<<<< HEAD
                '([0-9, ]+)นอน([0-9, ]+)น้ำ', 'นอน([0-9, ]+)น้ำ([0-9, ]+)', 
                '([0-9, ]+)bedroom([0-9, ]+) bathroom', '([0-9, ]+)bed([0-9, ]+)bath']
=======
                '([0-9, ]+)นอน([0-9, ]+)น้ำ', 'นอน([0-9, ]+)น้ำ([0-9, ]+)',
                '([0-9, ]+)bedroom([0-9, ]+) bathroom', '([0-9, ]+)bed([0-9, ]+)bath',]
>>>>>>> master
    bedroom = set()
    bathroom = set()
    for p in patterns:
        exp = re.compile(p)
        for i in exp.findall(detail):
            bed = [j for j in re.split(' ', re.sub(',', '', i[0])) if j != '' and int(j) < 10]
            bed = [bed[-1]] if len(bed) > 0 else None
            bath = [j for j in re.split(' ', re.sub(',', '', i[1])) if j != '' and int(j) < 10]
            bath = [bath[-1]] if len(bath) > 0 else None
            if bed is not None and bath is not None:
                bedroom.update(bed)
                bathroom.update(bath)
    if len(bedroom) > 1 or len(bathroom) > 1:
        return -1, -1
    bedroom = bedroom.pop() if len(bedroom) > 0 else None
    bathroom = bathroom.pop() if len(bathroom) > 0 else None
    return bedroom, bathroom


def extraction_floor_before(floor, ext_floor):
    if ext_floor == -1:
        return -1
    for i in range(len(floor)-1):
        point = 0
        if floor[i+1] == '':
            continue
        while floor[i+1][point] in ' 0123456789':
            point += 1
            if point >= len(floor[i+1]):
                break
        ext_floor_arr = floor[i+1][0:point]
        ext_floor_arr = re.split('[ /,]', ext_floor_arr)
        for value in ext_floor_arr:
            if value and ext_floor is None:
                ext_floor = value
            if value and ext_floor != value:
                return -1
    return ext_floor

def extraction_floor(detail):
    ext_floor = None
    all_floor = detail.split('จำนวนชั้น')
    lenght = len(all_floor)
    if lenght == 1:
        floor = detail.split('ชั้น')
        ext_floor = extraction_floor_before(floor, ext_floor)
    else:
        for f in all_floor[1:lenght-1]:
            floor = f.split('ชั้น')
            ext_floor = extraction_floor_before(floor, ext_floor)
    return ext_floor


def extraction(detail):
    # which field can't extract, return None
    # filter multiple value

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
