from multiprocessing import Process,Event
from time import time

#from topThread import globalMatrix
# workingThreads import WorkingThreads
import numpy

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
        t = 0
        for i in range(1,self.nbEpochs):
            print "Previous epoch : %f" %(time()-t)
            t = time()
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

    # Fonction permettant de gerer les acces concurrents
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

    # Fonction qui cree les indices pour une epch et qui les repartit
    def createOneShuffle(self):
        # print "shuffling, round %d" % self.round

        permRow = createPerm(self.nRows)
        permCol = createPerm(self.nCols)
        self.C = [[[] for _ in range(self.nWThread)] for _ in range(self.nWThread)]
        
        for (i,j) in self.om:
            a = self.nWThread*permRow[i]/self.nRows
            b = self.nWThread*permCol[j]/self.nCols
            self.C[a][b].append(i)
            self.C[a][b].append(j)
        
        print "Perm : Creation of C finished"

        for u in range(self.nWThread):
            for a in range(self.nWThread):
                b = (a + u) % self.nWThread
                self.pushToQueue(a, self.C[a][b])
                
            print "Perm : Creation of round %d finished" %u

    def write(self, buff, n):
        self.buffers[buff][self.bufferWrite[buff]] = n
        self.bufferWrite[buff] = (self.bufferWrite[buff] + 1) % self.bufferSize
        #print "writing in the buffer %d : wrote %d at %d" \
        #   % (buff, n, self.bufferWrite[buff])

    def pushToQueue(self, buff, l):
        n = len(l)
        self.write(buff, n)
        if (self.bufferWrite[buff] + n) >self.bufferSize:
            print "changeBuffer"
            self.bufferWrite[buff] = 0
        self.buffers[buff][self.bufferWrite[buff]:self.bufferWrite[buff]+n] = l
        self.bufferWrite[buff] = (self.bufferWrite[buff] + n) % self.bufferSize
        


def createPerm(N):
    perm = [i for i in range(N)]
    numpy.random.shuffle(perm)
    return perm

