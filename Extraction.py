import re
import string


def extraction_price(detail):
    patterns = ['([0-9,]+) บาท', 'ราคา ([0-9,]+)']
    price = set()
    for p in patterns:
        exp = re.compile(p)
        s = [float(re.sub(',', '', i)) for i in exp.findall(detail)]
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
    ext_size = extraction_size_before(detail.split('ตรม'), None)
    ext_size = extraction_size_before(detail.split('ตร.ม'), ext_size)
    ext_size = extraction_size_before(detail.split('ตารางเมตร'), ext_size)
    ext_size = extraction_size_before(detail.split('ตาราง.ม.'), ext_size)
    ext_size = extraction_size_before(detail.split('Square meters'), ext_size)
    ext_size = extraction_size_before(detail.split('sq.m.'), ext_size)
    ext_size = extraction_size_before(detail.split('Sq.M.'), ext_size)
    ext_size = extraction_size_before(detail.split('sqm.'), ext_size)
    ext_size = extraction_size_before(detail.split('Sq.m'), ext_size)
    ext_size = extraction_size_before(detail.split('SQ.M'), ext_size)
    ext_size = extraction_size_before(detail.split('sqm '), ext_size)
    ext_size = extraction_size_before(detail.split('Sqm.'), ext_size)
    ext_size = extraction_size_after(detail.split('ขนาด'), ext_size)
    ext_size = extraction_size_after(detail.split('พื้นที่'), ext_size)
    return ext_size


def extraction_tower_after(tower, ext_tower):
    if ext_tower == -1:
        return -1
    for i in range(len(tower)-1):
        point = 0
        if tower[i+1] == '':
            continue
        while tower[i+1][point] not in '1234567890 \r\n':
            point += 1
            if point >= len(tower[i+1]):
                break
        ext_tower_arr = tower[i+1][0:point]
        ext_tower_arr = re.split('[ /,]', ext_tower_arr)
        for value in ext_tower_arr:
            if value and ext_tower is None and (value in list(string.ascii_lowercase) or value in list(string.ascii_uppercase)):
                ext_tower = value
            if value and ext_tower != value and (value in list(string.ascii_lowercase) or value in list(string.ascii_uppercase)):
                return -1
    return ext_tower


def extraction_tower(detail):
    ext_tower = extraction_tower_after(detail.split('ตึก'), None)
    ext_tower = extraction_tower_after(detail.split('อาคาร'), ext_tower)
    return ext_tower


def extraction_bed_bath(detail):
    patterns = ['([0-9,]+) ห้องนอน ([0-9,]+) ห้องน้ำ', '([0-9,]+) นอน ([0-9,]+) น้ำ', 'ห้องนอน ([0-9,]+) ห้องน้ำ ([0-9,]+)', 'นอน ([0-9,]+) น้ำ ([0-9,]+)', 
                '([0-9,]+)ห้องนอน ([0-9,]+)ห้องน้ำ', '([0-9,]+)นอน ([0-9,]+)น้ำ', 'ห้องนอน([0-9,]+)ห้องน้ำ([0-9,]+)', 'นอน([0-9,]+)น้ำ([0-9,]+)', 
                '([0-9,]+) bedroom ([0-9,]+) bathroom', '([0-9,]+) bed ([0-9,]+) bath', 'bedroom ([0-9,]+) bathroom ([0-9,]+)', 'bed ([0-9,]+) bath ([0-9,]+)']
    bedroom = set()
    bathroom = set()
    for p in patterns:
        exp = re.compile(p)
        for i in exp.findall(detail):
            bedroom.update(i[0])
            bathroom.update(i[1])

    if len(bedroom) > 1 and len(bathroom) > 1:
        return -1, -1
    if len(bedroom) == 0 and len(bathroom) == 0:
        return None, None
    return bedroom.pop(), bathroom.pop()


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
