from permThread import PermThread
from workingThread import WorkingThread
from multiprocessing import Event, Value, RawArray, Lock
from preprocessing import preprocessDir
import numpy as np
from numpy.random import random
import matplotlib.pyplot as plt


def initThreads(nRows, nCols, nWorkingThreads, nbEpochs,
                om, r, mij, om_i, om_j, mu, alpha, dalpha, method, avg):
    # Concurrency tools
    eventFRold = Event()
    eventFEold = Event()
    eventFRnew = Event()
    eventFEnew = Event()
    counterFR = Value('i', 0, lock=False)
    counterFE = Value('i', 0, lock=False)
    lockFR = Lock()
    lockFE = Lock()

    # Process-specific data
    bufferSize = 6 * len(om)
    buffers = [RawArray('i', bufferSize) for _ in range(nWorkingThreads)]

    # Problem-specific data
    L = RawArray('f', nRows * r)
    rand = random(nRows * r)
    for i in range(nRows * r):
        L[i] = rand[i]
    R = RawArray('f', nCols * r)
    rand = random(nCols * r)
    for i in range(nCols * r):
        R[i] = rand[i]

    workingThreads = [WorkingThread(
        eventFRold, eventFRnew, eventFEold, eventFEnew,
        counterFR, counterFE,
        lockFR, lockFE, i,
        nWorkingThreads,
        (nRows, nCols), buffers[i], bufferSize,
        nbEpochs, L, R, mij, om_i, om_j,
        mu, alpha, dalpha, r, method, avg)
        for i in range(nWorkingThreads)]

    perm = PermThread(eventFEnew, eventFEold,
                      counterFE, lockFE,
                      nWorkingThreads,
                      buffers, bufferSize,
                      nRows, nCols, nbEpochs, om)

    return (perm, workingThreads)


def startAllThreads(perm, workingThreads):
    perm.start()
    for wT in workingThreads:
        wT.start()


def joinAllThreads(perm, workingThreads):
    perm.join()
    for wT in workingThreads:
        wT.join()


def getPrincipalSVD(L, nRows, r):
    from random import sample as random_sample
    rmax = max(int(2 * r * np.log(r)) + 1, nRows)
    L2 = L[random_sample(range(nRows), rmax)]
    s = np.linalg.svd(L2, compute_uv=False)
    return s[:r]


def profileForRank():
    nWorkingThreads = 1
    nbEpochs = 10
    nRows, nCols, om_i, om_j, mij, om, avg = preprocessDir(directory)
    r0 = max(1, int(1.0 * len(om) / (3 * (nRows + nCols))))
    r1 = 10 * r0
    L_h = np.zeros((r1 - r0, r0))
    R_h = np.zeros((r1 - r0, r0))
    print "r0 = %d" % r0

    for r in range(r0, r1):
        print "r = %d" % r
        (perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads, nbEpochs,
                                             om, r, mij, om_i, om_j, mu, alpha, dalpha,
                                             method, avg)
        perm.createOneShuffle()

        startAllThreads(perm, workingThreads)
        joinAllThreads(perm, workingThreads)
        print "Finished for r=%d" % r

        # Tests
        L = workingThreads[0].L
        R = workingThreads[0].R
        L = np.array(L).reshape(nRows, r)
        R = np.array(R).reshape(nCols, r)

        print "First SVD of L : %f" % L[0, 0]
        print "First SVD of R : %f" % R[0, 0]

        L_h[r - r0, :] = getPrincipalSVD(L, nRows, r)
        R_h[r - r0, :] = getPrincipalSVD(R, nCols, r)

    plt.plot(L_h[:, 0])
    plt.legend("SVD of L")
    plt.plot(R_h[:, 0])
    plt.legend("SVD of R")
    plt.show()


nWorkingThreads = 7
nbEpochs = 20
alpha = 0.05
dalpha = 0.8
mu = 0.00001
r = 30
beta = 5
method = "NUCLEAR_NORM"

directory = "ml-100k"

print "choosing r : "
profileForRank()


print "Lauching main thread"
nRows, nCols, om_i, om_j, mij, om, avg = preprocessDir(directory)
(perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads, nbEpochs,
                                     om, r, mij, om_i, om_j, mu, alpha, dalpha,
                                     method, avg)
perm.createOneShuffle()
# print workingThreads[0].printQueue()
# print workingThreads[1].printQueue()
# print workingThreads[2].printQueue()

startAllThreads(perm, workingThreads)
joinAllThreads(perm, workingThreads)
print "Exiting main thread"
# perm.event.wait()

print "printing matrix"

# Tests
L = workingThreads[0].L
R = workingThreads[0].R
L = np.array(L).reshape(nRows, r)
R = np.array(R).reshape(nCols, r)
matrix = 5 * np.dot(L, np.transpose(R))
fi = open(directory + "/u.test", "r")
err = 0
c = 0
for line in fi:
    c += 1
    l = line.split()
    i = int(l[0]) - 1
    j = int(l[1]) - 1
    note = int(l[2])
    err += (matrix[i, j] - note) ** 2

err /= c
err = np.sqrt(err)
