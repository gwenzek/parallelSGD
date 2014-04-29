from multiprocessing import Process, Queue


class WorkingThread(Process):

    def __init__(self, event, boolArray, index,
                 matrix, queueSize, maxIter):
        Process.__init__(self)
        self.event = event.Value
        self.boolArray = boolArray
        self.index = index
        self.queue = Queue(queueSize)
        self.maxIter = maxIter
        self.nIter = 0
        self.matrix = matrix.Value

    def run(self):
        print "Starting permThread"
        while self.hasNext():
            self.treatOneRound()
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
        print "Thread %d finished last" % self.index
        return True

    def treatOneRound(self):
        print "updating gradient"

    def hasNext(self):
        return not self.queue.isEmpty()
