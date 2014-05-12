from permThread import PermThread
from workingThread import WorkingThread
from workingThreadAlone import WorkingThreadAlone
from multiprocessing import Event, Value, RawArray, Lock
from preprocessing import preprocessDir
from numpy.random import random
import numpy as np
from time import time

# Initialisation de tous les Threads
def initThreads(nRows, nCols, nWorkingThreads, nbEpochs,om,r,mij,om_i,om_j,mu,alpha,dalpha,method,B,test,avg):
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
    bufferSize = 3*len(om)
    buffers = [RawArray('i', bufferSize) for _ in range(nWorkingThreads)]
    
    # Problem-specific data
    L = RawArray('f',nRows*r)
    rand = random(nRows*r)
    for i in range(nRows*r):
        L[i] =rand[i]
    R = RawArray('f',nCols*r)
    rand = random(nCols*r)
    for i in range(nCols*r):
        R[i] =rand[i]

    workingThreads = [WorkingThread(eventFRold,eventFRnew,eventFEold,eventFEnew, 
                                    counterFR,counterFE, 
                                    lockFR,lockFE, i,
                                    nWorkingThreads,
                                    (nRows, nCols), buffers[i], bufferSize,
                                    nbEpochs, L,R,mij,om_i,om_j,
                                    mu,alpha,dalpha,r,method,B,test,avg)
                     for i in range(nWorkingThreads)]
                         
    # Process pour tester l'algorithme avec remise
    Lalone = RawArray('f',nRows*r)
    rand = random(nRows*r)
    for i in range(nRows*r):
        Lalone[i] =rand[i]
    Ralone = RawArray('f',nCols*r)
    rand = random(nCols*r)
    for i in range(nCols*r):
        Ralone[i] =rand[i]
    workingThreadAlone = WorkingThreadAlone(eventFEold,eventFEnew,counterFE,lockFE, nWorkingThreads+1, nWorkingThreads,(nRows,nCols),
                 nbEpochs, L,R,mij,om_i,om_j,
            mu,alpha,dalpha,r, method,B)         
                      
    perm = PermThread(eventFEnew,eventFEold,
                 counterFE, lockFE,
                 nWorkingThreads,
                 buffers, bufferSize,
                 nRows, nCols, nbEpochs,om)
                 
    return (perm, workingThreads,workingThreadAlone)


def startAllThreads(perm, workingThreads,workingThreadAlone):
    perm.start()
    #workingThreadAlone.start()
    for wT in workingThreads:
        wT.start()


def joinAllThreads(perm, workingThreads,workingThreadAlone):
    perm.join()
    for wT in workingThreads:
        wT.join()
  # workingThreadAlone.join()


print "Lauching main thread"


nWorkingThreads = 2
nbEpochs = 20
alpha = 0.03
dalpha = 0.9
mu = 0.0001
r = 30
beta = 5
B = 1.5
method = "ETA_NORM"


#nRows = 1000
#nCols = 5000
#Lin = random((nRows,r))
#Rin = random((r,nCols))
#M = np.dot(Lin,Rin)
#M/=np.linalg.norm(M)
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
#for (i,j) in samples:
#    mij[(i,j)] = M[i,j]
#    
#    om_i[i] += 1
#    om_j[j] += 1
#    om.append((i,j))

#
# Choix du directory
directory = "ml-1m"
test,nRows,nCols,om_i,om_j,mij,om,avg = preprocessDir(directory)


t = time()
(perm, workingThreads,workingThreadAlone) = initThreads(nRows, nCols, nWorkingThreads, nbEpochs,
                        om,r,mij,om_i,om_j,mu,alpha,dalpha,method,B,test,avg)
perm.createOneShuffle()
#print workingThreads[0].printQueue()
#print workingThreads[1].printQueue()
#print workingThreads[2].printQueue()

startAllThreads(perm, workingThreads,workingThreadAlone)
joinAllThreads(perm, workingThreads,workingThreadAlone)
print "Exiting main thread"
#perm.event.wait()*
    
    
# Comparaion avec l'algorithme avec remise
for _ in range(nbEpochs):
    t = time()
    workingThreadAlone.treatOneRound()
    lwT = workingThreadAlone.L
    rwT = workingThreadAlone.R
    L = np.empty(nRows*r)
    R = np.empty(nCols*r)
    for i in range(len(L)):
        L[i] = lwT[i]
    
    for i in range(len(R)):
        R[i] = rwT[i]    
        
        
    DIV = 1
    matrix = np.dot(L.reshape(nRows,r),np.transpose(R.reshape(nCols,r)))
    
    
    #err = np.sqrt(((matrix-M)**2).mean())
    #print err
    
    for i in range(nRows):
        matrix[i]+=avg[i]
    matrix = DIV*matrix
    err = 0
    c = 0
    
    #fi = open(directory+"/u.test","r")
    #
    #for line in fi:
    #    l = line.split()
    #    i = int(l[0])-1
    #    j = int(l[1])-1
    #    note = int(l[2])
    #    try:
    #        err += (matrix[i,j]-note)**2
    #        c += 1
    #    except:
    #        print "error"
    #        pass
    
    for i in range(nRows):
        j = test[i][0][0]
        note = test[i][0][1]
        err += (matrix[i,j]-note)**2
        c += 1
        j = test[i][1][0]
        note = test[i][1][1]
        err += (matrix[i,j]-note)**2
        c += 1
            
    err /= c
    err = np.sqrt(err)
    print "RMSE : "+str(err)
    
    print "Duree de l'epoch : " +str(time() -t)
