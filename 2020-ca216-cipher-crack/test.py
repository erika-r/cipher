import queue
from threading import Thread
import time

def sample(number):
    print("running {}".format(number))
    time.sleep(2)
    print("this should come after ish")
    return "hello"

que = queue.Queue()

threads = []
for i in range(5):
    t = Thread(target=lambda q, arg1: q.put(sample(arg1)),args=(que,i))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

    result = que.get()  
    print(result)
#with concurrent.futures.ThreadPoolExecutor() as exc:
#    test = [exc.submit(sample,number) for number in range(4)]
