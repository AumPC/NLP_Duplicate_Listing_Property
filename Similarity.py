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
    # floor_score = WEIGHT['floor'] * different_numerical(pair[0]['floor'], pair[1]['floor'])
    floor_score = WEIGHT['floor'] * different_character(pair[0]['floor'], pair[1]['floor'])
    type_score = WEIGHT['type'] * different_character(pair[0]['type'], pair[1]['type'])
    return price_score + size_score + tower_score + floor_score + type_score

def minNum(a,b) :
    if(a > b) :
        return b
    return a

def isNumber(num) :
    try :
        float(num)
        return True
    except ValueError :
        return False

def bagOfWord(text) :
    wordList=word_tokenize(text,engine='newmm')
    bag = {}
    for i in wordList :
        if (i == ' ' or i == '\n' or isNumber(i)) :
            continue
        elif (i in bag) :
            bag[i] += 1
        else :
            bag[i] = 1
    return bag

def detail_similarity(textA,textB) :
    bagA = bagOfWord(textA)
    bagB = bagOfWord(textB)
    sizeA = 0
    sizeB = 0
    insc = 0
    for i in bagA :
        sizeA += bagA[i]
    for i in bagB :
        sizeB += bagB[i]
        if(i in bagA) :
            insc += minNum(bagA[i],bagB[i])
    return (1+insc)/(1+minNum(sizeA,sizeB))

# def detail_similarity(detail1, detail2):
#     # use bag of word here
#     # score = (1 + total_intersect_word)/(1 + total_word_in_shorter_detail)
#     return 0
