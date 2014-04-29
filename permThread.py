from multiprocessing import Process
from random import randint


class PermThread (Process):

    def __init__(self, event, boolArray, index, workingThreads,
                 nRows, nCols, maxIter):
        Process.__init__(self)
        self.event = event.Value
        self.workingThreads = workingThreads
        self.nRows = nRows
        self.nCols = nCols
        self.nThread = len(workingThreads)
        self.boolArray = boolArray
        self.index = index
        self.maxIter = maxIter
        self.nIter = 0

    def run(self):
        print "Starting permThread"
        while self.hasNext():
            self.createOneShuffle()

            if self.checkArray():
                self.event.set()
                self.event.clear()
            else:
                self.event.wait()
            self.nIter += 1
        print "Exiting permThread"

    def checkArray(self):
        self.boolArray[self.index] = True
        for b in self.boolArray:
            if not b:
                return False
        """Every one finished"""
        for i in range(1 + self.nThread):
            self.boolArray[i] = False
        print "!!! Perm is the last to finish !!!"
        return True

    def createOneShuffle(self):
        print "shuffling"
        permRow = createPerm(self.nRows)
        permCol = createPerm(self.nRows)
        for n in range(self.nThread):
            for i in range(n * self.nRows / self.nThread,
                          (n + 1) * self.nRows / self.nThread):
                for j in range(n * self.nCols / self.nThread,
                              (n + 1) * self.nCols / self.nThread):
                    self.workingThreads[n].queue.add((permRow[i], permCol[j]))

    def hasNext(self):
        return self.nIter >= self.maxIter


def createPerm(N):
    perm = [-1 for _ in range(N)]
    for i in range(N):
        j = randint(0, N - 1 - i)
        while perm[j] >= 0:
            j += 1
        perm[j] = i
    return perm
