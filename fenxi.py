import json
import numpy as np
filename = "CTC-SP2-1996-3.1-cln.swf.train_1.0"
with open(filename) as f:
    users = json.load(f)
us = {}
minmax_us = {}
c1 =200
c2 =200
def big(v,vs):
    for i,k in enumerate(vs):
        if v<k:
            return i-1
    return 0

def I(S,H):
    subs = np.arange(S.min(), (S.max()+1e-10)+(S.max()+1e-10-S.min())/c1, (S.max()+1e-10-S.min())/(c1-1e-10))
    runs = np.arange(H.min(), (H.max()+1e-10)+(H.max()+1e-10-H.min())/c2, (H.max()+1e-10-H.min())/(c2-1e-10))
    p = np.zeros(shape=[c1, c2])
    for i in range(S.shape[0]):
        row = big(S[i], subs)
        col = big(H[i], runs)
        p[row, col] += 1
    p /= p.sum()
    ps = p.sum(1).reshape(c1,1)
    pr = p.sum(0).reshape(1,c2)
    p_d = p/(ps.dot(pr)+1e-10)
    p_d_log = np.log(p_d)
    where_are_nan = np.isinf(p_d_log)
    p_d_log[where_are_nan] = 0
    p = p * p_d_log
    return p.sum()

def func(S,H):
    t = I(S,H)
    k = 0
    n = 10
    for i in range(n):
        np.random.shuffle(H)
        kk = I(S,H)
        k+=kk
    return t - k/n

S=np.arange(20)
H=np.arange(20)
print(func(S,H))

for u,v in users.items():
    S = np.zeros(len(v))
    H = np.zeros(len(v))
    for i,k in enumerate(v):
        S[i] = k[1]
        H[i] = k[3]
    # S = np.array(v)[:,1]
    # H = np.array(v)[:,3]
    # print(temp)
    # S = np.array(temp[:,0]).reshape(len(v))
    # H = np.array(temp[:,1]).reshape(len(v))
    # H = np.log2(H)
    if len(v)>1:
        us[u] = func(S,H)

v_sum = 0
count1, count2 = 0, 0
for u,v in us.items():
    if v<0:
        count1+=1
    else:
        count2+=1
    print(v)
    v_sum+=v

print(count1,count2,v_sum,v_sum/(count2+count1))



