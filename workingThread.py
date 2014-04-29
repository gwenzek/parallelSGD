from multiprocessing import Process
from time import sleep


def printMatrix(matrix, nRows, nCols):
    print "-------"
    for i in range(nRows):
        print "[",
        for j in range(nCols):
            print matrix[nRows * i + j],
        print "]"


class WorkingThread(Process):

    def __init__(self,
                 event, boolArray, index, nThread,
                 dim, sharedBuffer, bufferSize,
                 maxIter, globalMatrix):
        Process.__init__(self)
        self.event = event
        self.boolArray = boolArray
        self.index = index

        self.buffer = sharedBuffer
        self.bufferRead = 0
        self.bufferSize = bufferSize

        self.nRows, self.nCols = dim

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
                printMatrix(self.globalMatrix, self.nRows, self.nCols)
                self.event.set()
                self.event.clear()

            else:
                print "Thread %d waiting..." % self.index
                self.event.wait()

            print "Thread %d resuming, %d" \
                % (self.index, self.bufferRead)
            self.nIter += 1

        sleep(1)
        print "Exiting Thread %d " % self.index

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
        print "Thread %d | Round %d | queue %d" \
            % (self.index, self.nIter, self.peek())

        n = self.read()
        for _ in range(n):
            i = self.read()
            j = self.read()
            self.globalMatrix[self.nRows * i + j] = self.index + 1
            #print "Thread %d : (%d, %d)" % (self.index, i, j)

        printMatrix(self.globalMatrix, self.nRows, self.nCols)

    def read(self):
        n = self.buffer[self.bufferRead]
        self.bufferRead = (self.bufferRead + 1) % self.bufferSize
        #print "reading from the buffer %d : read %d at %d" \
        #    % (self.index, n, (self.bufferRead - 1))
        return n

    def peek(self):
        return self.buffer[self.bufferRead]

    def printQueue(self):
        oldRead = self.bufferRead
        n = self.read()
        for _ in range(n):
            print "(%d, %d)" % (self.read(), self.read()),
        print "*"
        self.bufferRead = oldRead

    def hasNext(self):
        return self.nIter < self.maxIter
