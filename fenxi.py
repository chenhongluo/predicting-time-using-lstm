import json
import numpy as np
filename = "CTC-SP2-1996-3.1-cln.swf.train_1.0"
with open(filename) as f:
    users = json.load(f)
us = {}
minmax_us = {}
c1 =5
c2 =5
def big(v,vs):
    for i,k in enumerate(vs):
        if v<k:
            return i-1
    return 0

def I(S,R):
    subs = np.arange(S.min(), S.max(), (S.max()-S.min()+1e-5)/(c1+1))
    runs = np.arange(R.min(), R.max(), (R.max()-R.min()+1e-5)/(c2+1))
    p = np.zeros(shape=[c1, c2])
    for s,r in zip(S,R):
        p[big(s, subs), big(r, runs)] += 1
    p /= p.sum()
    ps = p.sum(1).reshape(c1,1)
    pr = p.sum(0).reshape(1,c2)
    p_d = p/(ps.dot(pr)+1e-10)
    p_d_log = np.log(p/p_d)
    where_are_nan = np.isnan(p_d_log)
    p_d_log[where_are_nan] = 0
    p = p * p_d_log
    return p.sum()

def func(S,R):
    t = I(S,R)
    k = 0
    n = 10
    for i in range(n):
        np.random.shuffle(R)
        k+=I(S,R)
    return t - k/n

for u,v in users.items():
    temp = np.array(v)
    S = temp[:,1]
    R = temp[:,3]
    # R = np.log2(R)
    us[u] = func(S,R)

v_sum = 0
count1, count2 = 0, 0
for u,v in us.items():
    if v<0:
        count1+=1
    else:
        count2+=1
    v_sum+=v

print(count1,count2,v_sum,v_sum/(count2+count1))



