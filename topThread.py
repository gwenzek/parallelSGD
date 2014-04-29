from permThread import PermThread
from workingThread import WorkingThread, printMatrix
from multiprocessing import Event, Array, RawArray


def initThreads(nRows, nCols, nWorkingThreads, maxIter, bufferSize=1000):
    globalMatrix = RawArray('f', 9 * 9)

    syncEvent = Event()
    boolArray = Array('b', nWorkingThreads + 1, lock=True)

    buffers = [RawArray('i', bufferSize) for _ in range(nWorkingThreads)]

    workingThreads = [WorkingThread(syncEvent, boolArray, i, nWorkingThreads,
                                    (nRows, nCols), buffers[i], bufferSize,
                                    maxIter, globalMatrix)
                      for i in range(nWorkingThreads)]
    perm = PermThread(syncEvent, boolArray, nWorkingThreads,
                      workingThreads, buffers, bufferSize,
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
    print workingThreads[0].queue
    print workingThreads[1].queue
    print workingThreads[2].queue


print "Lauching main thread"

nRows = 9
nCols = 9
nWorkingThreads = 3

maxIter = 3
(perm, workingThreads) = initThreads(nRows, nCols, nWorkingThreads,
                                     maxIter)
perm.createOneShuffle()
print workingThreads[0].printQueue()
print workingThreads[1].printQueue()
print workingThreads[2].printQueue()

startAllThreads(perm, workingThreads)
print "Exiting main thread"
joinAllThreads(perm, workingThreads)
#perm.event.wait()

print "printing matrix"
printMatrix(workingThreads[0].globalMatrix, nRows, nCols)
