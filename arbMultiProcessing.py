from multiprocessing import Manager,Process,JoinableQueue, Event as mpEvent
import time
def testFunc(args):
    print('testFunc recieved',args[0])
    goManageArgs2(testFunc2,args[0],2)
    # for arg in args:
    #     print(arg)
        # time.sleep(1)

def testFunc2(arg):
    print('testfunc2 ',arg)
    time.sleep(1)
    return
    # for arg in args:
        # print(arg)
        # time.sleep(1)

def threadMagic(someFunc,args):
    someFunc(args)
    return
from random import uniform
def goProc(q):
    while not q.empty():
        if q.empty():
            break
        args = q.get(timeout=1)
        # if args == None:
        #     break
        time.sleep(uniform(.2,.6))
        print('go proc args:',args, 'approx qsize: ',q.qsize())
        threadMagic(args[0], args[1:])
        #q.task_done()
        if q.empty():
            break
def goProc_joinQueue(q):
    while True:#not q.empty():
        if q.empty():
            break
        args = q.get()
        if args == None:
            break
        #stagger processes just a tad
        time.sleep(uniform(.2,.6))
        print('go proc args:',args)
        threadMagic(args[0], args[1:])
        q.task_done()
        if q.empty():
            break

def goManageArgs_new(whatFunc,args,numProcs):
    """Arbitrarily multiprocess a function
    whatFunc is your helper function that expands the args 
        and sends it to the actual func that does the work. 
    args must be in list format, but each arg is arbitrary e.g.
        args = [[a,b,c],[1,2,3]]
        args = [file1,file2]
        args = [1,2,3,4]
        etc.
    NumProcs: create this many processes to do something with the Args
    No error handleing is performed by this function or file.
    """
    q = JoinableQueue()
    stop_event = mpEvent()
    procs = []
    for _ in range(numProcs):
        p = Process(target=goProc_joinQueue,args=(q,stop_event))
        p.start()
        procs.append(p)
    for arg in args:
        q.put((whatFunc,arg))
    q.join()
    stop_event.set()        
    for p in procs:
        p.join()
    
def goManageArgs(whatFunc,args,numProcs):
    """Arbitrarily multiprocess a function
    whatFunc is your helper function that expands the args 
        and sends it to the actual func that does the work. 
    args must be in list format, but each arg is arbitrary e.g.
        args = [[a,b,c],[1,2,3]]
        args = [file1,file2]
        args = [1,2,3,4]
        etc.
    NumProcs: create this many processes to do something with the Args
    No error handleing is performed by this function or file.
    """
    with Manager() as manager:
        q = manager.Queue()
        for arg in args:
            q.put((whatFunc,arg))
        procs = []
        for _ in range(numProcs):
            p = Process(target=goProc,args=(q,))
            procs.append(p)
        for p in procs:
            p.start()
        for p in procs:
            p.join()

def goManageArgs2(whatFunc,args,numProcs):
    """ Same as goManageArgs, but in case you want to split the work again
    This means the work has to go into a different queue.
    Arbitrarily multiprocess a function
    whatFunc is your helper function that expands the args 
        and sends it to the actual func that does the work. 
    args must be in list format, but each arg is arbitrary e.g.
        args = [[a,b,c],[1,2,3]]
        args = [file1,file2]
        args = [1,2,3,4]
        etc.
    NumProcs: create this many processes to do something with the Args
    No error handleing is performed by this function or file.
    """
    with Manager() as manager:
        q = manager.Queue()
        for arg in args:
            q.put((whatFunc,arg))
        procs = []
        for _ in range(numProcs):
            p = Process(target=goProc,args=(q,))
            procs.append(p)
        for p in procs:
            p.start()
        for p in procs:
            p.join()
#goManageArgs(testFunc,testArgs,2)