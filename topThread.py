from permThread import PermThread
from workingThread import WorkingThread
from multiprocessing import Event, Value, Array


def initThreads(nRows, nCols, nWorkingThreads, matrix, maxIter):
    syncEvent = Event()
    boolArray = Array(bool, nWorkingThreads + 1)
    queueSize = nRows * nCols / nWorkingThreads / nWorkingThreads
    sharedMatrix = Value(matrix)
    workingThreads = [WorkingThread(event, boolArray, i,
                      sharedMatrix, queueSize, maxIter)
                      for i in range(nWorkingThreads)]
    perm = PermThread(syncEvent, boolArray, 0, workingThreads,
                      nRows, nCols, maxIter)


def main():
