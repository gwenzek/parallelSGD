from multiprocessing import Process,Event
from random import randint

#from topThread import globalMatrix
# workingThreads import WorkingThreads


class PermThread (Process):

    def __init__(self,
                 eventFEnew,eventFEold,
                 counterFE, lockFE,
                 nWThreads,
                 buffers, bufferSize,
                 nRows, nCols, nbEpochs,om
                 ):
        
        Process.__init__(self)
        
        # Concurrency tools
        self.counterFE = counterFE
        self.eventFEnew = eventFEnew
        self.eventFEold = eventFEold
        self.lockFE = lockFE

        # I/O with working threads
        self.buffers = buffers
        self.bufferSize = bufferSize
        self.bufferWrite = [0 for _ in range(nWThreads)]
        
        # Problem-specific data        
        self.nRows = nRows
        self.nCols = nCols
        self.nWThread = nWThreads
        self.om = om
        self.nbEpochs = nbEpochs


    def run(self):
        print "Starting permThread"
        
        for i in range(1,self.nbEpochs):
            print "permThread on epoch : %d" % i 
            self.createOneShuffle()
            if self.checkArray(self.lockFE,self.counterFE,self.eventFEold,self.nWThread+1):
                print "Perm finished last"
                self.eventFEnew.set()
            else:
                print "Perm waiting..."
                self.eventFEnew.wait()
            self.eventFEnew,self.eventFEold=self.eventFEold,self.eventFEnew
        print "Exiting permThread"
        self.eventFEnew.set()

    def checkArray(self,lock,counter,event,value):
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
        # print "!!! Perm is the last to finish !!!"
        # return True

    def createOneShuffle(self):
        # print "shuffling, round %d" % self.round

        permRow = createPerm(self.nRows)
        permCol = createPerm(self.nCols)
        C = [[[] for _ in range(self.nWThread)] for _ in range(self.nWThread)]
        
        for (i,j) in self.om:
            a = self.nWThread*permRow[i]/self.nRows
            b = self.nWThread*permCol[i]/self.nCols
            C[a][b].append((i,j))

        for u in range(self.nWThread):
            for a in range(self.nWThread):
                b = (a + u) % self.nWThread
                self.pushToQueue(a, C[a][b])

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
