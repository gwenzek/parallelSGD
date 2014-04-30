from multiprocessing import Process
from random import randint

#from topThread import globalMatrix
# workingThreads import WorkingThreads


class PermThread (Process):

    def __init__(self,
                 event, counter, lock,
                 index, workingThreads,
                 buffers, bufferSize,
                 nRows, nCols, maxIter):
        Process.__init__(self)
        self.event = event
        #self.workingThreads = workingThreads
        self.nRows = nRows
        self.nCols = nCols
        self.nThread = len(workingThreads)

        self.counter = counter
        self.lock = lock

        self.index = index
        self.maxIter = maxIter
        self.nIter = 0
        self.round = 0
        self.buffers = buffers
        self.bufferSize = bufferSize
        self.bufferWrite = [0 for _ in range(self.nThread)]

    def run(self):
        print "Starting permThread"
        while self.hasNext():
            print "permThread on iter : %d" % self.nIter
            self.createOneShuffle()

            if self.checkArray():
                print "Perm finished last"
                self.event.set()
                self.event.clear()
            else:
                print "Perm waiting..."
                self.event.wait()
            self.nIter += 1
        print "Exiting permThread"

    def checkArray(self):
        self.lock.acquire()
        self.counter.value += 1
        if self.counter.value > self.nThread:
            self.counter.value = 0
            self.lock.release()
            return True
        else:
            self.lock.release()
        # self.boolArray[self.index] = True
        # for b in self.boolArray:
        #     if not b:
        #         return False
        # """Every one finished"""
        # for i in range(1 + self.nThread):
        #     self.boolArray[i] = False
        # print "!!! Perm is the last to finish !!!"
        # return True

    def createOneShuffle(self):
        print "shuffling, round %d" % self.round
        if self.round == 0:
            self.permRow = createPerm(self.nRows)
            self.permCol = createPerm(self.nRows)

        for nn in range(self.nThread):
            roundQueue = []
            n = (nn + self.round) % self.nThread
            for i in range(n * self.nRows / self.nThread,
                          (n + 1) * self.nRows / self.nThread):
                for j in range(nn * self.nCols / self.nThread,
                              (nn + 1) * self.nCols / self.nThread):
                    roundQueue.append((self.permRow[i], self.permCol[j]))
                    #print "perm : %d | %d | (%d, %d)" % (self.round, nn, i, j)
            self.pushToQueue(nn, roundQueue)

        self.round = (self.round + 1) % self.nThread

    def hasNext(self):
        return self.nIter <= self.maxIter

    def write(self, buff, n):
        self.buffers[buff][self.bufferWrite[buff]] = n
        self.bufferWrite[buff] = (self.bufferWrite[buff] + 1) % self.bufferSize
        #print "writing in the buffer %d : wrote %d at %d" \
        #   % (buff, n, self.bufferWrite[buff])

    def pushToQueue(self, buff, l):
        self.write(buff, len(l))
        for (i, j) in l:
            self.write(buff, i)
            self.write(buff, j)


def createPerm(N):
    perm = [-1 for _ in range(N)]
    for i in range(N):
        j = randint(0, N - 1 - i)
        while perm[j] >= 0:
            j += 1
        perm[j] = i
    return perm
