import threading
import time

exitFlag = 0


class myThread (threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print "Starting " + self.name
        print_time(self.name, self.counter, self.counter)
        print "Exiting " + self.name

    def prepare(self, count):
        self.counter = count


def print_time(threadName, delay, counter):
    while counter > 0:
        #if exitFlag:
           # thread.exit()
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1

# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

thread1.join()
thread2.join()

print "Both thread finished"
thread1.prepare(5)
thread2.prepare(5)
thread1.start()
thread2.start()
print "Exiting Main Thread"
