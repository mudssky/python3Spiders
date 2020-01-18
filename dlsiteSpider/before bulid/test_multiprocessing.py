import multiprocessing
import os
class SendeventProcess(multiprocessing.Process):
    def __init__(self, resultQueue):
        self.resultQueue = resultQueue
        multiprocessing.Process.__init__(self)
        self.start()

    def run(self):
        print ('SendeventProcess')
        self.resultQueue.put((1, 2))
        print ('SendeventProcess')


if __name__ == '__main__':
    # On Windows calling this function is necessary.
    # On Linux/OSX it does nothing.
    multiprocessing.freeze_support()
    print ('main')
    resultQueue = multiprocessing.Queue()
    SendeventProcess(resultQueue)
    print ('main')
    os.system('pause')
