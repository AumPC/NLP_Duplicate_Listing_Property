test_score = [  [1,2,0.6],
                [1,3,0.2],
                [1,4,0.1],
                [2,3,0.3],
                [2,4,0.1],
                [3,4,0.5] ]
def group_find(score):
    node = []
    for i in score:
        if not i[0] in node:
            node.append(i[0])
        if not i[1] in node:
            node.append(i[1])
    threshold = 0.5 # <---- tune threshold here
    ans={}
    for i in node:
        ans[i]=i
    for i in score:
        if i[2] >= threshold:
            a=i[0]
            b=i[1]
            while ans[a] != a:
                tmp = a
                a = ans[a]
                ans[tmp] = ans[a]
            while ans[b] != b:
                tmp = b
                b = ans[b]
                ans[tmp] = ans[b]
            ans[b] = ans[a]
    group = {}
    for i in node:
        tmp = i
        while tmp != ans[tmp]:
            tmp = ans[tmp]
        if tmp in group:
            group[tmp].append(i)
        else :
            group[tmp] = [i]
    return group

if __name__ == '__main__':
    group = group_find(test_score)
    # print(group)
    for g in group:
        print(group[g])