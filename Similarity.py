# pip install pythainlp
from pythainlp.tokenize import word_tokenize
from pythainlp.ner import thainer

def different_numerical(a, b):
    if a == None and b == None:
        return 1
    if a == None or b == None:
        return 0
    if a == 0 and b == 0:
        return 1
    return 1 - (abs(a - b) * 2 / (a + b))

def different_character(a, b):
    # Levenshtein distance
    metrix = []
    for i in range(len(a) + 1):
        m = []
        for j in range(len(b) + 1):
            m.append(0)
        metrix.append(m)
    for i in range(len(a) + 1):
        metrix[i][0] = i
    for i in range(len(b) + 1):
        metrix[0][i] = i
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i] == b[j]:
                metrix[i+1][j+1] = metrix[i][j]
            else:
                metrix[i+1][j+1] = min(metrix[i][j], metrix[i+1][j], metrix[i][j+1]) + 1
    return 1 - (metrix[len(a)][len(b)] / max(len(a), len(b)))

def field_similarity(pair, WEIGHT):
    price_score = WEIGHT['price'] * different_numerical(pair[0]['price'][0], pair[1]['price'][0])
    size_score = WEIGHT['size'] * different_numerical(pair[0]['size'], pair[1]['size'])
    tower_score = WEIGHT['tower'] * different_character(pair[0]['tower'], pair[1]['tower'])
    floor_score = WEIGHT['floor'] * different_character(pair[0]['floor'], pair[1]['floor'])
    type_score = WEIGHT['type'] * different_character(pair[0]['type'], pair[1]['type'])
    return price_score + size_score + tower_score + floor_score + type_score


def is_number(num) :
    try :
        float(num)
        return True
    except ValueError :
        return False

def bag_of_word(text) :
    word_list = word_tokenize(text, engine='newmm')
    bag = {}
    for word in word_list :
        if word == ' ' or word == '\n' or is_number(word) :
            continue
        elif word in bag :
            bag[word] += 1
        else :
            bag[word] = 1
    return bag

def detail_similarity(text_A,text_B) :
    bag_A = bag_of_word(text_A)
    bag_B = bag_of_word(text_B)
    size_A = 0
    size_B = 0
    intersect = 0
    for word in bag_A :
        size_A += bag_A[word]
    for word in bag_B :
        size_B += bag_B[word]
        if word in bag_A :
            intersect += min(bag_A[word],bag_B[word])
    return (1+intersect)/(1+min(size_A,size_B))