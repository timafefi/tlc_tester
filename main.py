import test
import plot
from threading import Thread

f = open("log.txt", "a+")
f.close()
f = open("freeheap.txt", "a+")
f.close()
t = Thread(target=test.start_test)
t.start()
plot.start_plot()
t.join()
