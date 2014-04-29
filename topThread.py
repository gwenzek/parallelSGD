from permThread import PermThread
from workingThread import WorkingThread
from multiprocessing import Event, Array
import numpy


def initThreads(nRows, nCols, nWorkingThreads, maxIter):
    globalMatrix = [numpy.zeros(9) for _ in range(9)]

    syncEvent = Event()
    boolArray = Array('b', nWorkingThreads + 1, lock=True)
    queueSize = nRows * nCols / nWorkingThreads / nWorkingThreads
    print queueSize
    #sharedMatrix = Value(type(matrix), 1, lock=False)
    workingThreads = [WorkingThread(syncEvent, boolArray, i, nWorkingThreads,
                      queueSize, maxIter, globalMatrix)
                      for i in range(nWorkingThreads)]
    perm = PermThread(syncEvent, boolArray, nWorkingThreads, workingThreads,
                      nRows, nCols, maxIter)
    return (perm, workingThreads)


def startAllThreads(perm, workingThreads):
    perm.start()
    for wT in workingThreads:
        wT.start()

def joinAllThreads(perm, workingThreads):
    perm.join()
    for wT in workingThreads:
        wT.join()

def main():
    print "Lauching main thread"
    nRows = 9
    nCols = 9
    nWorkingThreads = 3

    maxIter = 1
    (perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads,
                                         maxIter)
    perm.createOneShuffle()
    print workingThreads[0].queue
    print workingThreads[1].queue
    print workingThreads[2].queue
    startAllThreads(perm, workingThreads)
    print "Exiting main thread"
    perm.event.wait()


def printMatrix(matrix):
    print "-------"
    for row in matrix:
        print row

print "Lauching main thread"
nRows = 9
nCols = 9
nWorkingThreads = 3

maxIter = 1
(perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads,
                                     maxIter)
perm.createOneShuffle()
print workingThreads[0].queue
print workingThreads[1].queue
print workingThreads[2].queue
startAllThreads(perm, workingThreads)
print "Exiting main thread"
#joinAllThreads(perm, workingThreads)
perm.event.wait()

print "printing different matrices"
printMatrix(workingThreads[0].globalMatrix)
printMatrix(workingThreads[1].globalMatrix)
printMatrix(workingThreads[2].globalMatrix)
