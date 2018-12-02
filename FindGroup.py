from collections import defaultdict
from time import time

def group_find(group, score):
    expand_group = defaultdict(list, group)
    start = time()
    ans = {i: i for i in {s[0] for s in score}.union({s[1] for s in score})}
    for i in score:
        while ans[i[0]] != ans[ans[i[0]]]:
            ans[i[0]] = ans[ans[i[0]]]
        while ans[i[1]] != ans[ans[i[1]]]:
            ans[i[1]] = ans[ans[i[1]]]
        ans[i[0]] = ans[i[1]]
    for i in ans:
        while ans[i] != ans[ans[i]]:
            ans[i] = ans[ans[i]]
        expand_group[ans[i]].append(i)
    return expand_group, time()-start

if __name__ == '__main__':
    test_score = [[1, 2, 0.6],
                  [1, 3, 0.2],
                  [1, 4, 0.1],
                  [2, 3, 0.3],
                  [2, 4, 0.1],
                  [3, 4, 0.5]]
    group, time = group_find({}, test_score)
    print(group)
    for g in group:
        print(group[g])
