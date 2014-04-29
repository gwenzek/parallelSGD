from multiprocessing import Process
from topThread import globalMatrix


class WorkingThread(Process):

    def __init__(self, event, boolArray, index, nThread,
                 queueSize, maxIter):
        Process.__init__(self)
        self.event = event
        self.boolArray = boolArray
        self.index = index
        self.queue = []
        self.queueSize = queueSize
        self.maxIter = maxIter
        self.nIter = 0
        self.nThread = nThread

    def run(self):
        print "Starting Thread %d " % self.index
        while self.hasNext():
            self.treatOneRound()
            if self.checkArray():
                print "Thread %d finished last" % self.index
                print globalMatrix
                self.event.set()
                self.event.clear()
            else:
                print "Thread %d waiting..." % self.index
                self.event.wait()
            print "Thread %d resuming" % self.index
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
        return True

    def treatOneRound(self):
        print "Thread %d : updating gradient, round %d" \
            % (self.index, self.nIter)
        for _ in range(max(self.queueSize)):
            (i, j) = self.queue.pop(0)
            globalMatrix[i, j] = self.index

    def pushToQueue(self, i, j):
        self.queue.append((i, j))

    def hasNext(self):
        return self.nIter < self.maxIter
