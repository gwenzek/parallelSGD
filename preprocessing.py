def preprocess(dataFile, infoFile):
    info = open(infoFile, 'r')
    nUsers = int(info.readline().split()[0])
    nMovies = int(info.readline().split()[0])
    info.close()

    omegaUsers = [0 for _ in range(nUsers)]
    omegaMovies = [0 for _ in range(nMovies)]
    M = dict()
    om=[]
    avg = 0.0
    for line in open(dataFile, 'r'):
        l = line.split()
        (i, j, note) = (int(l[0]) - 1, int(l[1]) - 1, int(l[2]))
        M[(i, j)] = note/5.0
        omegaUsers[i] += 1
        omegaMovies[j] += 1
        om.append((i,j))
        avg += note/5.0

    return(nUsers, nMovies, omegaUsers, omegaMovies, M, om, avg/len(om), )


def preprocessDir(directory):
    return preprocess(directory + "/u.data", directory + "/u.info")
