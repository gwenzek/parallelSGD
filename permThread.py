from multiprocessing import Process, Value, Array


class permThread (Process):
    def __init__(self, event, boolArray, index, workingThreads, nRows, nCols):
        Process.__init__(self)
        self.event = event.Value
        self.workingThreads = workingThreads
        self.nRows = nRows
        self.nCols = nCols
        self.nThread = len(workingThreads)
        self.boolArray = boolArray
        self.index = index

    def run(self):
        print "Starting permThread"
        self.createOneShuffle()
        self.boolArray[self.index] = True
        if checkArray(self.boolArray):
            self.event.set()
            self.event.clear()
        print "Exiting permThread"

    def checkArray(boolArray):
        for b in boolArray:
            if not b:
                return False
        """Every one finished"""
        for i in range(1+nThread):
            boolArray[i] = False
        return True


    def createOneShuffle(self):
        print "shuffling"
