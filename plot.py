import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import matplotlib.dates as mdates


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


def animate(i):
    data = ''
    with open('freeheap.txt', 'r') as f:
        data = f.read()
    lines = data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if line:
            x, y = line.split(',')
            xs.append(datetime.strptime(x, "%d-%m %H:%M:%S"))
            ys.append(int(y))
    ax.clear()
    ax.xaxis.set_major_locator(plt.LinearLocator())
    plt.xticks(rotation=45)
    ax.plot(xs, ys)
    # Formatting the x - axis with date labels
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M:%S'))
    plt.gcf().autofmt_xdate()
    plt.xlabel('Time (s)')
    plt.ylabel('Free heap (bytes)')
    plt.title('Free heap monitor')


def start_plot():
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

if __name__ == '__main__':
    start_plot()
