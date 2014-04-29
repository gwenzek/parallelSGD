from multiprocessing import Process
from globalVar import globalMatrix, printMatrix
from time import time, sleep


class WorkingThread(Process):

    def __init__(self, event, boolArray, index, nThread,
                 queueSize, maxIter, globalMatrix):
        Process.__init__(self)
        self.event = event
        self.boolArray = boolArray
        self.index = index
        self.queue = []
        self.queueSize = queueSize
        self.maxIter = maxIter
        self.nIter = 0
        self.nThread = nThread
        self.globalMatrix = globalMatrix

    def run(self):
        print "Starting Thread %d " % self.index
        while self.hasNext():
            self.treatOneRound()
            if self.checkArray():
                print "Thread %d finished last" % self.index
                print self.globalMatrix
                self.event.set()
                self.event.clear()
            else:
                # print "Thread %d waiting..." % self.index
                self.event.wait()
            # print "Thread %d resuming" % self.index
            self.nIter += 1
        sleep(5)
        print "Exiting Thread %d " % self.index
        print self.globalMatrix

    def checkArray(self):
        self.boolArray[self.index] = True
        for b in self.boolArray:
            if not b:
                return False
        """Every one finished"""
        for i in range(1 + self.nThread):
            self.boolArray[i] = False
        return True

    def treatOneRound(self):
        print "%f Thread %d |round %d | queue %d" \
            % (time(), self.index, self.nIter, len(self.queue))

        for _ in range(min(self.queueSize, len(self.queue))):
            (i, j) = self.queue.pop(0)
            self.globalMatrix[i][j] = self.index + 1
        print self.globalMatrix

    def pushToQueue(self, i, j):
        self.queue.append((i, j))

    def hasNext(self):
        return self.nIter < self.maxIter
