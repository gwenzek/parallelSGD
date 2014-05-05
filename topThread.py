from permThread import PermThread
from workingThread import WorkingThread, printMatrix
from multiprocessing import Event, Value, RawArray, Lock
from preprocessing import preprocessDir
from numpy.random import random
import numpy as np
from time import time


def initThreads(nRows, nCols, nWorkingThreads, nbEpochs,om,r,mij,om_i,om_j,mu,alpha,dalpha,method,avg):
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
    bufferSize = 2*len(om)
    buffers = [RawArray('i', bufferSize) for _ in range(nWorkingThreads)]
    
    # Problem-specific data
    L = RawArray('f',nRows*r)
    rand = random(nRows*r)
    for i in range(nRows*r):
        L[i] = rand[i]
    R = RawArray('f',nCols*r)
    rand = random(nCols*r)
    for i in range(nCols*r):
        R[i] = rand[i]

    workingThreads = [WorkingThread(eventFRold,eventFRnew,eventFEold,eventFEnew, 
                                    counterFR,counterFE, 
                                    lockFR,lockFE, i,
                                    nWorkingThreads,
                                    (nRows, nCols), buffers[i], bufferSize,
                                    nbEpochs, L,R,mij,om_i,om_j,
                                    mu,alpha,dalpha,r,method,avg)
                      for i in range(nWorkingThreads)]
                      
    perm = PermThread(eventFEnew,eventFEold,
                 counterFE, lockFE,
                 nWorkingThreads,
                 buffers, bufferSize,
                 nRows, nCols, nbEpochs,om)
                 
    return (perm, workingThreads)


def startAllThreads(perm, workingThreads):
    perm.start()
    for wT in workingThreads:
        wT.start()


def joinAllThreads(perm, workingThreads):
    perm.join()
    for wT in workingThreads:
        wT.join()


print "Lauching main thread"


nWorkingThreads = 7
nbEpochs = 40
alpha = 0.05
dalpha = 0.8
mu = 0.00001
r = 30
beta = 5
method = "NUCLEAR_NORM"

#nRows = 1000
#nCols = 5000
#L = random((nRows,r))
#R = random((r,nCols))
#M = np.dot(L,R)
#samples = []
#mat = [[True for i in range(nCols)]for j in range(nRows)]
#nb_samples = beta * r *(nRows+nCols-r)
#while(nb_samples>0):
#    i = np.random.randint(0,nRows)
#    j = np.random.randint(0,nCols)
#    if mat[i][j]:
#        samples.append((i,j))
#        mat[i][j]=False
#        nb_samples-=1
#print len(samples)
#om_i = [0 for _ in range(nRows)]
#om_j = [0 for _ in range(nCols)]
#mij = dict()
#om=[]
#avg = 0.0
#for (i,j) in samples:
#    mij[(i,j)] = M[i,j]
#    
#    om_i[i] += 1
#    om_j[j] += 1
#    om.append((i,j))
#    avg+=M[i,j]


directory = "data10M"
nRows,nCols,om_i,om_j,mij,om,avg = preprocessDir(directory)
(perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads, nbEpochs,
                        om,r,mij,om_i,om_j,mu,alpha,dalpha,method,avg)
perm.createOneShuffle()
#print workingThreads[0].printQueue()
#print workingThreads[1].printQueue()
#print workingThreads[2].printQueue()

startAllThreads(perm, workingThreads)
joinAllThreads(perm, workingThreads)
print "Exiting main thread"
#perm.event.wait()

print "printing matrix"

# Tests
#L = workingThreads[0].L
#R = workingThreads[0].R
#L = np.array(L)
#R = np.array(R)
#matrix = np.dot(L.reshape(nRows,r),np.transpose(R.reshape(nCols,r)))
#err = np.sqrt(((matrix-M)**2).mean())
#print err

#matrix = 5*np.dot(L.reshape(nRows,r),np.transpose(R.reshape(nCols,r)))
#fi = open(directory+"/u.test","r")
#err = 0
#c = 0
#for line in fi:
#    c += 1
#    l = line.split()
#    i = int(l[0])-1
#    j = int(l[1])-1
#    note = int(l[2])
#    err += (matrix[i,j]-note)**2
#
#err /= c
#err = np.sqrt(err)
