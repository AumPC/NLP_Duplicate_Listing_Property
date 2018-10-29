import re

def extraction_price(detail):
    patterns = ['([0-9,]*) บาท', 'ราคา ([0-9,]*)']
    price = set()
    for p in patterns:
        exp = re.compile(p)
        price.update(exp.findall(detail))
    print(price)
    return price

def extraction_size_before(size, ext_size):
    for i in range(len(size)-1):
        point = len(size[i])-1
        while size[i][point] in '0123456789 /,.':
            point -= 1
            if point < 0:
                break
        ext_size_arr = size[i][point+1:]
        ext_size_arr = re.split(' |/|,', ext_size_arr)
        for value in ext_size_arr:
            if value and ext_size == None:
                ext_size = value
            if value and ext_size != value:
                return -1
    return ext_size

def extraction_size_after(size, ext_size):
    for i in range(len(size)-1):
        point = 0
        while size[i+1][point] in '0123456789 /,.':
            point += 1
            if point >= len(size[i+1]):
                break
        ext_size_arr = size[i+1][0:point]
        ext_size_arr = re.split(' |/|,', ext_size_arr)
        for value in ext_size_arr:
            if value and ext_size == None:
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
    for i in range(len(tower)-1):
        point = 0
        while tower[i+1][point] not in '1234567890 ':
            point += 1
            if point >= len(tower[i+1]):
                break
        ext_tower_arr = tower[i+1][0:point]
        ext_tower_arr = re.split(' |/|,', ext_tower_arr)
        for value in ext_tower_arr:
            if value and ext_tower == None and value in ['A','B','C','D']:
                ext_tower = value
            if value and ext_tower != value and value in ['A','B','C','D']:
                return -1
    return ext_tower

def extraction_tower(detail):
    ext_tower = extraction_tower_after(detail.split('ตึก'), None)
    ext_tower = extraction_tower_after(detail.split('อาคาร'), ext_tower)
    print(ext_tower)
    return ext_tower

def extraction(detail):
    # which field can't extract, return None
    # filter multiple value

    ext = {'price':[None, None], 'size':None, 'tower':None, 'floor':None, 'type':None, 'bedroom':None, 'bathroom':None}    
    if not detail : 
        return ext

    # ner = thainer()
    # g = word_tokenize(detail,engine='newmm')
    # print(g)
    # text = ner.get_ner(detail)
    # print(text, '\n\n\n')
    # for word in text:
    #     print(word[0] , '\n')
    return ext
