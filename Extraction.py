import re
import string


def extraction_price(detail):
    patterns = ['([0-9, ]+)บาท', 'ราคา([0-9, ]+)']
    price = set()
    for p in patterns:
        exp = re.compile(p)
        s = [float(re.sub('[, ]', '', i)) for i in exp.findall(detail) if re.sub('[, ]', '', i) != '']
        price.update(s)

    price = [i for i in price if 1000 < i < 1000000]
    if len(price) > 1:
        return -1
    if len(price) == 0:
        return [None, None]
    return [price.pop(), None]


def extraction_size_before(size, ext_size):
    if ext_size == -1:
        return -1
    for i in range(len(size)-1):
        point = len(size[i])-1
        while size[i][point] in '0123456789 /,.':
            point -= 1
            if point < 0:
                break
        ext_size_arr = size[i][point+1:]
        ext_size_arr = re.split('[ /,]', ext_size_arr)
        for value in ext_size_arr:
            if value == '.':
                continue
            if value and ext_size is None:
                ext_size = value
            if value and ext_size != value:
                return -1
    return ext_size


def extraction_size_after(size, ext_size):
    if ext_size == -1:
        return -1
    for i in range(len(size)-1):
        point = 0
        while size[i+1][point] in '0123456789 /,.':
            point += 1
            if point >= len(size[i+1]):
                break
        ext_size_arr = size[i+1][0:point]
        ext_size_arr = re.split('[ /,]', ext_size_arr)
        for value in ext_size_arr:
            if value and ext_size is None:
                ext_size = value
            if value and ext_size != value:
                return -1
    return ext_size


def extraction_size(detail):
    pattern = [
        'ตรม', 'ตร.ม', 'ตร ม', 'ตร. ม',
        'ตารางเมตร', 'ตารางวา', 'ตาราง.ม.',
        'Square meters', 'Square meters',
        'SQ.M', 'SQ.m', 'Sq.M', 'Sq.m', 'sQ.M', 'sQ.m', 'sq.M', 'sq.m',
        'SQM ', 'SQm ', 'SqM ', 'Sqm ', 'sQM ', 'sQm ', 'sqM ', 'sqm ',
        'SQM.', 'SQm.', 'SqM.', 'Sqm.', 'sQM.', 'sQm.', 'sqM.', 'sqm.',
        'sqm,'
    ]
    ext_size = None
    for pat in pattern:
        ext_size = extraction_size_before(detail.split(pat), ext_size)
    ext_size = extraction_size_after(detail.split('sq.m.):'), ext_size)

    # ext_size = extraction_size_after(detail.split('ขนาด'), ext_size)
    # ext_size = extraction_size_after(detail.split('พื้นที่'), ext_size)
    return ext_size


def extraction_tower_after(tower, ext_tower):
    if ext_tower == -1:
        return -1
    thai_building = ['เอ', 'บี', 'ซี', 'ดี', 'อี', 'เอฟ', 'จี']
    number_building = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    name_building = set( thai_building + number_building + list(string.ascii_uppercase) + list(string.ascii_lowercase))
    for i in range(len(tower)-1):
        point = 0
        if tower[i+1] == '':
            continue
        found = 0
        while point < len(tower[i+1]) and (tower[i+1][point] not in ' \r\n' or found != 2):
            if tower[i+1][point] in '0123456789' and found <= 1:
                found = 1
            elif tower[i+1][point] not in '\r\n ':
                found = 2
            point += 1
        ext_tower_arr = tower[i+1][0:point]
        if 'ตึก' in ext_tower_arr or 'อาคาร' in ext_tower_arr or 'คัน' in ext_tower_arr or 'ชั้น' in ext_tower_arr:
            continue
        ext_tower_arr = re.split('[ /,]', ext_tower_arr)
        for value in ext_tower_arr:
            if value and ext_tower is None and value in name_building:
                ext_tower = value
            if value and ext_tower != value and value in name_building:
                return -1
    return ext_tower


def extraction_tower(detail):
    ext_tower = extraction_tower_after(detail.split('ตึก'), None)
    ext_tower = extraction_tower_after(detail.split('อาคาร'), ext_tower)
    return ext_tower


def extraction_bed_bath(detail):
    patterns = ['([0-9, ]+)ห้องนอน([0-9, ]+)ห้องน้ำ', 'ห้องนอน([0-9, ]+)ห้องน้ำ([0-9, ]+)',
                '([0-9, ]+)นอน([0-9, ]+)น้ำ', 'นอน([0-9, ]+)น้ำ([0-9, ]+)', 
                '([0-9, ]+)bedroom([0-9, ]+) bathroom', '([0-9, ]+)bed([0-9, ]+)bath',]
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
    if len(bedroom) > 1:
        bedroom = -1
    elif len(bedroom) == 0:
        bedroom = None
    else:
        bedroom = bedroom.pop()

    if len(bathroom) > 1:
        bathroom = -1
    elif len(bathroom) == 0:
        bathroom = None
    else:
        bathroom = bathroom.pop()

    return bedroom, bathroom



def extraction(detail):
    # which field can't extract, return None
    # filter multiple value

    ext = {'price': [None, None], 'size': None, 'tower': None, 'floor': None, 'type': None, 'bedroom': None, 'bathroom': None}
    if not detail:
        return ext
    
    ext['price'] = extraction_price(detail)
    ext['size'] = extraction_size(detail)
    ext['tower'] = extraction_tower(detail)
    ext['bedroom'], ext['bathroom'] = extraction_bed_bath(detail)
    if ext['price'] == -1 or ext['size'] == -1 or ext['tower'] == -1 or ext['bedroom'] == -1 or ext['bathroom'] == -1:
        return -1

    return ext
