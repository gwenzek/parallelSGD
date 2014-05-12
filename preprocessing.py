import numpy.random as nr

DIV= 1
TEST = 2


def preprocess(dataFile, infoFile):
    info = open(infoFile, 'r')
    nUsers = int(info.readline().split()[0])
    nMovies = int(info.readline().split()[0])
    info.close()

    omegaUsers = [0 for _ in range(nUsers)]
    omegaMovies = [0 for _ in range(nMovies)]
    M = dict()
    ind = 0
    om=[]
    avg = [0 for _ in range(nUsers)]
    compt = [0 for _ in range(nUsers)]
    c = 0
    for line in open(dataFile,'r'):
        c+=1
        if (c%100000==0):
            print c
        l = line.split("::")
        (i, j, note) = (int(l[0]) - 1, int(l[1]) - 1, float(l[2]))
        avg[i] += note/DIV
        compt[i]+=1
    
    avg = [avg[i]/compt[i] for i in range(nUsers)]
    test = [[[0,0],[0,0]] for _ in range(nUsers)]
    for i in range(nUsers):
        u = nr.randint(0,compt[i])
        test[i][0][0] = u
        v = u
        while(v==u):
            v = nr.randint(0,compt[i])
        test[i][1][0] = v
        
    c=0
    compt2 = [0 for _ in range(nUsers)]
    for line in open(dataFile, 'r'):
        c+=1
        if (c%100000==0):
            print c
        l = line.split("::")
        (i, j, note) = (int(l[0]) - 1, int(l[1]) - 1, float(l[2]))
        if compt2[i] != test[i][0][0] and compt2[i] != test[i][1][0]:
            M[(i, j)] = note/DIV-avg[i]
            omegaUsers[i] += 1
            omegaMovies[j] += 1
            om.append((i,j))
        else:
            if test[i][0][0]==compt2[i]:
                test[i][0][0] = j
                test[i][0][1] = note

            if test[i][1][0]==compt2[i]:
                test[i][1][0] = j
                test[i][1][1] = note  
                
        compt2[i]+=1
        

    return(test,nUsers, nMovies, omegaUsers, omegaMovies, M,om,avg)


def preprocessDir(directory):
    return preprocess(directory + "/u.data", directory + "/u.info")
