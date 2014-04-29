from multiprocessing import Process, Value, Array


class permThread (Process):

    def __init__(self, event, boolArray, index,
                 matrix, queue, maxIter):
        Process.__init__(self)
        self.event = event.Value
        self.boolArray = boolArray
        self.index = index
        self.queue = queue
        self.maxIter = maxIter
        self.nIter = 0
        self.matrix = matrix.Value

    def run(self):
        print "Starting permThread"
        while self.hasNext():
            self.treatOneRoundShuffle()
            if self.checkArray():
                self.event.set()
                self.event.clear()
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

    def treatOneRoundShuffle(self):
        print "updating gradient"

    def hasNext(self):
        return not self.queue.isEmpty()
