from multiprocessing import Process
import numpy
import numpy.linalg as nl

class WorkingThread(Process):

    def __init__(self,
                 eventFRold,eventFRnew,eventFEold,eventFEnew, 
                 counterFR,counterFE, 
                 lockFR,lockFE, index, nWThread, dim,
                 sharedBuffer, bufferSize,
                 nbEpochs, L,R,mij,om_i,om_j,
            mu,alpha,dalpha,r, method,B,test,avg
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
        self.avg=avg
        self.test = test
        self.B = B
        self.method = method
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
        self.nL = numpy.empty(0)
        self.nR = numpy.empty(0)

    def run(self):
        #print "Starting Thread %d " % self.index

        for _ in range(self.nbEpochs):
            for roun in range(self.nWThread):
                self.treatOneRound()
                if self.checkArray(self.lockFR,self.counterFR,self.eventFRold,self.nWThread):
                    #print "Thread %d finished last" % self.index
                    print "ROUND " + str(roun+1)
                    self.eventFRnew.set()
                    

                else:
                    #print "Thread %d waiting..." % self.index
                    self.eventFRnew.wait()
                    #print "Thread %d resuming, %d" \
                       # % (self.index, self.peek())
                
                self.eventFRnew,self.eventFRold=self.eventFRold,self.eventFRnew
                
            
            if self.checkArray(self.lockFE,self.counterFE,self.eventFEold,self.nWThread+1):
                self.printRMSEEpoch()
               # print "Epoch : Thread %d finished last" % self.index
                self.eventFEnew.set()
            else:
                #print "Epoch : Thread %d waiting..." % self.index
                self.eventFEnew.wait()
               # print "Epoch : Thread %d resuming, %d" \
                    #    % (self.index, self.peek())
            self.eventFEnew,self.eventFEold=self.eventFEold,self.eventFEnew
            self.alpha = self.dalpha * self.alpha


        print "Exiting Thread %d " % self.index

    # Fonction gerant l'acces concurrent a un compteur
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
        # return True

    # Traite tous les indices d'un round
    def treatOneRound(self):
        
        
        self.indices = self.read() 
        i = 0
        old = True
        #print "index : " +str(self.index) + " couples a traiter : "+ str(n)
        for ind in self.indices:
            if old:
                i = ind
                old = False
                continue
            else:
                j = ind
                old=True
            self.nL = numpy.array(self.L[i*self.r:(i+1)*self.r])
            self.nR = numpy.array(self.R[j*self.r:(j+1)*self.r])
            if self.method == "NUCLEAR_NORM":
                    fp = self.fprime((i,j),numpy.dot(self.nL,self.nR))
                    if(str(fp)=="nan" or str(fp) == "nan" or str(fp)=="inf" or str(fp) == "inf" or str(fp)=="-inf" or str(fp) == "-inf"):
                        print numpy.dot(self.nL,self.nR)
                        print self.nL
                        print self.nR
                        assert(True==False)
                    self.nL = (1-self.mu*self.alpha/self.om_i[i])*self.nL-\
                        self.alpha*fp*self.nR
                    self.nR = (1-self.mu*self.alpha/self.om_j[j])*self.nR-\
                      self.alpha*fp*self.nL
                    self.L[i*self.r:(i+1)*self.r] = self.nL
                    self.R[j*self.r:(j+1)*self.r] = self.nR
                      
#                    for ind in range(self.r):
#                        newL = (1-self.mu*self.alpha/self.om_i[i])*self.L[i*self.r+ind]-\
#                        self.alpha*fp*self.R[j*self.r+ind]
#                        newR = (1-self.mu*self.alpha/self.om_j[j])*self.R[j*self.r+ind]-\
#                        self.alpha*fp*self.L[i*self.r+ind]
#                        if(newL>10**20 or newR>10**20):
#                            print self.multiply(i,j,True)
#                            assert(True==False)
#                        if(str(newL)=="nan" or str(newR) == "nan" or str(newL)=="inf" or str(newR) == "inf" or str(newL)=="-inf" or str(newR) == "-inf"):
#                            print self.index
#                            print self.multiply(i,j,True)
#                            assert(True==False)
#                        self.L[i*self.r+ind] = newL
#                        self.R[j*self.r+ind] = newR
            #print "Thread %d : (%d, %d)" % (self.index, i, j)
            elif self.method == "ETA_NORM":
                fp = self.fprime((i,j),numpy.dot(self.nL,self.nR))
                if(str(fp)=="nan" or str(fp) == "nan" or str(fp)=="inf" or str(fp) == "inf" or str(fp)=="-inf" or str(fp) == "-inf"):
                        print numpy.dot(self.nL,self.nR)
                        print self.nL
                        print self.nR
                        assert(True==False)
                self.nL =self.piB(self.nL-self.alpha*fp*self.nR)
                self.nR = self.piB(self.nR-self.alpha*fp*self.nL)
                self.L[i*self.r:(i+1)*self.r] = self.nL
                self.R[j*self.r:(j+1)*self.r] = self.nR
            
        #printMatrix(self.globalMatrix, self.nRows, self.nCols)
        
    def piB(self,v):
        nv = nl.norm(v)
        if(nv**2>self.B):
            return numpy.sqrt(self.B)*v/nv
        else:
            return v
        
    def fprime(self,ind,val):
        return 2*(val-self.mij[ind])
            
    def read(self):
        n = self.buffer[self.bufferRead]
        self.bufferRead = (self.bufferRead + 1) % self.bufferSize
        if(self.bufferRead + n) >self.bufferSize:
            self.bufferRead = 0
            print "changeBuffer " + str(self.index)
        u = self.bufferRead
        self.bufferRead = (self.bufferRead +n) %self.bufferSize
        #print "reading from the buffer %d : read %d at %d" \
        #    % (self.index, n, (self.bufferRead - 1))
        return self.buffer[u:u+n]

    def peek(self):
        return self.buffer[self.bufferRead]

    def printQueue(self):
        oldRead = self.bufferRead
        n = self.read()
        for _ in range(n):
            print "(%d, %d)" % (self.read(), self.read()),
        print "*"
        self.bufferRead = oldRead
        
    #Fonction affichant le temps mis pour l'epoch et le rmse

    def printRMSEEpoch(self):
        L = numpy.empty(self.nRows*self.r)
        R = numpy.empty(self.nCols*self.r)
        for i in range(len(L)):
            L[i] = self.L[i]
        
        for i in range(len(R)):
            R[i] = self.R[i]    
            
            
        DIV = 1
        matrix = numpy.dot(L.reshape(self.nRows,self.r),numpy.transpose(R.reshape(self.nCols,self.r)))
        
        
        #err = np.sqrt(((matrix-M)**2).mean())
        #print err
        
        for i in range(self.nRows):
            matrix[i]+=self.avg[i]
        matrix = DIV*matrix
        err = 0
        c = 0
        
        #fi = open(directory+"/u.test","r")
        #
        #for line in fi:
        #    l = line.split()
        #    i = int(l[0])-1
        #    j = int(l[1])-1
        #    note = int(l[2])
        #    try:
        #        err += (matrix[i,j]-note)**2
        #        c += 1
        #    except:
        #        print "error"
        #        pass
        
        for i in range(self.nRows):
            j = self.test[i][0][0]
            note = self.test[i][0][1]
            err += (matrix[i,j]-note)**2
            c += 1
            j = self.test[i][1][0]
            note = self.test[i][1][1]
            err += (matrix[i,j]-note)**2
            c += 1
                
        err /= c
        err = numpy.sqrt(err)
        print "RMSE : "+str(err)
        
