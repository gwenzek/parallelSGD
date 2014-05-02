from multiprocessing import Process


def printMatrix(matrix, nRows, nCols):
    print "-------"
    for i in range(nRows):
        print "[",
        for j in range(nCols):
            print matrix[nRows * i + j],
        print "]"


class WorkingThread(Process):

    def __init__(self,
                 eventFRold, eventFRnew, eventFEold, eventFEnew,
                 counterFR, counterFE,
                 lockFR, lockFE, index, nWThread, dim,
                 sharedBuffer, bufferSize,
                 nbEpochs, nwThread,
                 L, R, mij, om_i, om_j,
                 mu, alpha, dalpha, r
                 ):
        Process.__init__(self)

        # Concurrency tools
        self.eventFRold = eventFRold
        self.eventFEold = eventFEold
        self.eventFRnew = eventFRnew
        self.eventFEnew = eventFEnew
        self.counterFR = counterFR
        self.counterFE = counterFE
        self.lockFR = lockFR
        self.lockFE = lockFE

        # Process-specific data
        self.index = index
        self.buffer = sharedBuffer
        self.bufferRead = 0
        self.bufferSize = bufferSize

        # Problem-specific data
        self.nRows, self.nCols = dim
        self.nbEpochs = nbEpochs
        self.nWThread = nWThread
        self.L = L
        self.R = R
        self.mij = mij
        self.om_i = om_i
        self.om_j = om_j
        self.mu = mu
        self.alpha = alpha
        self.dalpha = dalpha
        self.r = r

    def run(self):
        print "Starting Thread %d " % self.index

        for _ in range(self.nbEpochs):
            for _ in range(self.nWThread):
                self.treatOneRound()
                if self.checkArray(self.lockFR, self.counterFR, self.eventFRold, self.nWThread):
                    print "Thread %d finished last" % self.index
                    self.eventFRnew.set()

                else:
                    print "Thread %d waiting..." % self.index
                    self.eventFRnew.wait()
                    print "Thread %d resuming, %d" \
                        % (self.index, self.peek())

                self.eventFRnew, self.eventFRold = self.eventFRold, self.eventFRnew

            if self.checkArray(self.lockFE, self.counterFE, self.nWThread + 1):
                print "Epoch : Thread %d finished last" % self.index
                self.eventFEnew.set()
            else:
                print "Epoch : Thread %d waiting..." % self.index
                self.eventFEnew.wait()
                print "Epoch : Thread %d resuming, %d" \
                    % (self.index, self.peek())
            self.eventFEnew, self.eventFEold = self.eventFEold, self.eventFEnew

        print "Exiting Thread %d " % self.index

    def checkArray(self, lock, counter, event, value):
        lock.acquire()
        counter.value += 1
        if counter.value == value:
            event.clear()
            counter.value = 0
            lock.release()
            return True
        else:
            lock.release()
            return False

        # self.boolArray[self.index] = True
        # for b in self.boolArray:
        #     if not b:
        #         return False
        # """Every one finished"""
        # for i in range(1 + self.nThread):
        #     self.boolArray[i] = False
        # return True

    def treatOneRound(self):

        n = self.read()
        for _ in range(n):
            i = self.read()
            j = self.read()
            if self.method == "NUCLEAR_NORM":
                    fp = self.fprime((i, j), self.multiply(i, j))
                    for ind in range(self.r):
                        newL = (1 - self.mu * self.alpha / self.om_i[i]) * self.L[i * self.r + ind] -\
                            self.alpha * fp * self.R[j * self.r + ind]
                        newR = (1 - self.mu * self.alpha / self.om_j[j]) * self.R[j * self.r + ind] -\
                            self.alpha * fp * self.L[i * self.r + ind]
                        self.L[i * self.r + ind] = newL
                        self.R[i * self.r + ind] = newR
            # print "Thread %d : (%d, %d)" % (self.index, i, j)

        #printMatrix(self.globalMatrix, self.nRows, self.nCols)

    def multiply(self, i, j):
        res = 0
        for ind in range(self.r):
            res += L[i * self.r + ind] * R[j * self.r + ind]
        return res

    def fprime(ind, val):
        return 2 * (val - self.mij[ind])

    def read(self):
        n = self.buffer[self.bufferRead]
        self.bufferRead = (self.bufferRead + 1) % self.bufferSize
        # print "reading from the buffer %d : read %d at %d" \
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
