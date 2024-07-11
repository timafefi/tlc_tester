import test
import plot
from threading import Thread

t = Thread(target=test.start_test)
t.start()
plot.start_plot()
t.join()
