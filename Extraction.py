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
    if len(price) > 2:
        return -1
    if not price:
        return None
    return [price[0], price[-1]]


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
    ext_size_arr = [ext_size for ext_size in ext_size_arr if ext_size]
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
    ext_size_arr = [ext_size for ext_size in ext_size_arr if ext_size]
    return ext_size_arr


def extraction_size(detail):
    prefix_keyword = ['ตรม', 'ตร.ม', 'ตารางเมตร', 'ตาราง.ม.', 'Square meters', 'sq.m.', 'Sq.M.', 'sqm.', 'Sq.m', 'SQ.M', 'sqm ', 'Sqm.']
    postfix_keyword = ['ขนาด', 'พื้นที่']
    ext_size = list(set(extraction_size_before(detail, prefix_keyword) + extraction_size_after(detail, postfix_keyword)))
    if len(ext_size) > 1:
        return -1
    if not ext_size:
        return None
    return ext_size[0]


def extraction_tower(detail):
    keyword = ['ตึก', 'อาคาร']
    ext_tower_arr = []
    for key in keyword:
        tower = detail.split(key)
        for i in range(len(tower) - 1):
            point = 0
            if tower[i + 1] == '':
                continue
            while tower[i + 1][point] not in '1234567890 \r\n':
                point += 1
                if point >= len(tower[i + 1]):
                    break
            ext_tower_arr += re.split('[ /,]', tower[i + 1][0:point])
    ext_tower_arr = list(set(ext_tower for ext_tower in ext_tower_arr if ext_tower in list(string.ascii_letters)))
    if len(ext_tower_arr) > 1:
        return -1
    if not ext_tower_arr:
        return None
    return ext_tower_arr[0]


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

    ext = {'price': None, 'size': None, 'tower': None, 'floor': None, 'type': None, 'bedroom': None, 'bathroom': None}
    if not detail:
        return ext
    ext['price'] = extraction_price(detail)
    ext['size'] = extraction_size(detail)
    ext['tower'] = extraction_tower(detail)
    ext['bedroom'], ext['bathroom'] = extraction_bed_bath(detail)
    if ext['price'] == -1 or ext['size'] == -1 or ext['tower'] == -1 or ext['bedroom'] == -1 or ext['bathroom'] == -1:
        return -1
    return ext
