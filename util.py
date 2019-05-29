import json
class st(object):
    def __init__(self,name):
        self.name = name
        pass

    def recode(self,v):
        pass

    def display(self):
        pass

class st1(st):
    def __init__(self,name):
        super(st1,self).__init__(name)
        self.min = 1e8
        self.max = -1e8

    def recode(self, v):
        self.min = min(self.min, v)
        self.max = max(self.max, v)

    def display(self):
        print("%s:min=%.2f,max=%.2f"%(self.name,self.min,self.max))

class st2(st):
    def __init__(self,name):
        super(st2, self).__init__(name)
        self.s = {}
        self.sub = st1(name)
    def recode(self,v):
        if v not in self.s.keys():
            self.s[v] = 0
        self.s[v] = self.s[v] + 1
        self.sub.recode(v)
    def display(self):
        print("%s:min=%.2f,max=%.2f,len=%d"%(self.name,self.sub.min,self.sub.max,len(self.s)))
    def mma(self):
        return [self.name,self.sub.min,self.sub.max,self.sub.max-self.sub.min,len(self.s)]

# Job Number -- a counter field, starting from 1.
# Submit Time -- in seconds. The earliest time the log refers to is zero, and is usually the submittal time of the first job. The lines in the log are sorted by ascending submittal times. It makes sense for jobs to also be numbered in this order.
# Wait Time -- in seconds. The difference between the job's submit time and the time at which it actually began to run. Naturally, this is only relevant to real logs, not to models.
# Run Time -- in seconds. The wall clock time the job was running (end time minus start time).
# Number of Allocated Processors -- an integer. In most cases this is also the number of processors the job uses; if the job does not use all of them, we typically don't know about it.
# Average CPU Time Used -- both user and system, in seconds. This is the average over all processors of the CPU time used, and may therefore be smaller than the wall clock runtime. If a log contains the total CPU time used by all the processors, it is divided by the number of allocated processors to derive the average.
# Used Memory -- in kilobytes. This is again the average per processor.
# Requested Number of Processors.
# Requested Time. This can be either runtime (measured in wallclock seconds), or average CPU time per processor (also in seconds) -- the exact meaning is determined by a header comment. In many logs this field is used for the user runtime estimate (or upper bound) used in backfilling. If a log contains a request for total CPU time, it is divided by the number of requested processors.
# Requested Memory (again kilobytes per processor).
# Status 1 if the job was completed, 0 if it failed, and 5 if cancelled. If information about chekcpointing or swapping is included, other values are also possible. See usage note below. This field is meaningless for models, so would be -1.
# User ID -- a natural number, between one and the number of different users.
# Group ID -- a natural number, between one and the number of different groups. Some systems control resource usage by groups rather than by individual users.
# Executable (Application) Number -- a natural number, between one and the number of different applications appearing in the workload. in some logs, this might represent a script file used to run jobs rather than the executable directly; this should be noted in a header comment.
# Queue Number -- a natural number, between one and the number of different queues in the system. The nature of the system's queues should be explained in a header comment. This field is where batch and interactive jobs should be differentiated: we suggest the convention of denoting interactive jobs by 0.
# Partition Number -- a natural number, between one and the number of different partitions in the systems. The nature of the system's partitions should be explained in a header comment. For example, it is possible to use partition numbers to identify which machine in a cluster was used.
# Preceding Job Number -- this is the number of a previous job in the workload, such that the current job can only start after the termination of this preceding job. Together with the next field, this allows the workload to include feedback as described below.
# Think Time from Preceding Job

class data_deal(object):
    def __init__(self):
        self.names = ["job number","submit time","wait time","run time","precessor number"," Average CPU Time Used",
                      "memory","requested processor num",
                      "requested time","request memory",
                      "Status","User ID",
                      "Group ID" ,"Executable (Application) Number","queue number","part numbar","None","None"]
        self.sts = [st2(self.names[i]) for i in range(18)]
        self.valid_count = 0
    def readline(self,line):
        if type(line) != list or len(line) != 18:
            print("error line")
        for i in range(18):
            self.sts[i].recode(line[i])
        self.valid_count += (1 if line[10] == 1 else 0)
    def display(self):
        for i in range(18):
            self.sts[i].display()
        print("ok jobs number:", self.valid_count)
    def mma(self):
        return [self.sts[i].mma() for i in range(18)]

def cc(v,min,max):
    return (v-min)/(max-min)

def data_convert():
    filename = "CTC-SP2-1996-3.1-cln.swf"
    p = 1.0
    max_cpus = None

    dd = data_deal()
    lines = []
    lines_deal = []
    with open(filename,'r') as f:
        while 1:
            line = f.readline()
            if line == "":
                break
            line=line[0:-1]
            line = line.split(' ')
            line = list(filter(lambda t:t!="",line))
            line = [int(float(x)) for x in line]
            dd.readline(line)
            if line[10] == 1:
            # if 1:
                lines.append(line)
    submit_time = lines[0][1]
    infos = dd.mma()
    with open(filename + ".index", 'w') as f:
        json.dump(infos,f)
    with open(filename+".deal_original",'w') as f,open(filename+".train_%.1f"%(p),'w') as f_train,\
            open(filename+".test_%.1f"%(p),'w') as f_test:
        print("infos count:%d,max cpu count:%d,max run time:%d,max request run time:%d "
              "user count:%d,group count:%d,app count:%d,infos per user:%.2f,,infos per group:%.2f,infos per job:%.2f"
              %(dd.valid_count,infos[4][2],infos[3][2],infos[8][2],infos[11][4],infos[12][4],
                infos[13][4],dd.valid_count/infos[11][4],dd.valid_count/infos[12][4],dd.valid_count/infos[13][4]))
        for l in lines:
            tt = [cc(l[i],0,infos[i][2]) for i in range(18)]
            temp = [l[0], l[1],
                    l[2], l[3],
                    cc(l[4], 0, max_cpus if max_cpus != None else infos[4][2]),
                    tt[5], tt[6], cc(l[7], 0, max_cpus if max_cpus != None else infos[7][2]),
                    tt[8], tt[9], l[10], l[11], l[12], l[13], l[14], l[15], l[16], l[17], l[3] / l[8]]
            # temp=[l[0],cc(l[1]-submit_time,0,infos[1][3]),
            #       l[2],tt[3],
            #       cc(l[4],0,max_cpus if max_cpus!=None else infos[4][2]),
            #       tt[5],tt[6],cc(l[7],0,max_cpus if max_cpus!=None else infos[7][2]),
            #       tt[8],tt[9],l[10],l[11],l[12],l[13],l[14],l[15],l[16],l[17],l[3]/l[8]]
            lines_deal.append(temp)
            # submit_time = l[1]
            # f.write(temp)
            # f.write('\n')
        def write_data(data,f):
            user_dict = {}
            for line in data:
                if line[11] not in user_dict.keys():
                    user_dict[line[11]] = []
                user_dict[line[11]].append(line)
            def takeSecond(elem):
                return elem[1]
            for v in user_dict.values():
                v.sort(key=takeSecond)
            json.dump(user_dict,f)

        size_train = int(len(lines_deal) * p)
        train_data = lines_deal[0:size_train]
        test_data = lines_deal[size_train:len(lines_deal)]
        write_data(train_data,f_train)
        write_data(test_data,f_test)

data_convert()