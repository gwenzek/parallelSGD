from permThread import PermThread
from workingThread import WorkingThread
from multiprocessing import Event, Array
import numpy as np


def initThreads(nRows, nCols, nWorkingThreads, maxIter):
    syncEvent = Event()
    boolArray = Array('b', nWorkingThreads + 1, lock=False)
    queueSize = nRows * nCols / nWorkingThreads / nWorkingThreads
    #sharedMatrix = Value(type(matrix), 1, lock=False)
    workingThreads = [WorkingThread(syncEvent, boolArray, i, nWorkingThreads,
                      queueSize, maxIter)
                      for i in range(nWorkingThreads)]
    perm = PermThread(syncEvent, boolArray, nWorkingThreads, workingThreads,
                      nRows, nCols, maxIter)
    return (perm, workingThreads)


def startAllThreads(perm, workingThreads):
    perm.start()
    for wT in workingThreads:
        wT.start()


def main():
    nRows = 9
    nCols = 9
    nWorkingThreads = 3

    maxIter = 4
    (perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads,
                                         maxIter)
    perm.createOneShuffle()
    startAllThreads(perm, workingThreads)
    print "Exiting main thread"

global globalMatrix
globalMatrix = np.zeros((9, 9))
main()
print globalMatrix
