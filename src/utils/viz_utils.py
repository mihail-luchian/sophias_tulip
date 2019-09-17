import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import utils.data_utils as data

def animate_images(data):
    fig = plt.figure()
    ims = []
    for d in data:
        im = plt.imshow(d, animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(
        fig, ims, interval=35, blit=True)

    plt.show()


def animate_plots_y(plots, interval=35):

    fig, ax = plt.subplots()
    line, = ax.plot(plots[0])

    def init():
        return line,

    def animate(i):
        line.set_ydata(plots[i])  # update the data.
        return line,

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, interval=interval, blit=True,frames=len(plots),repeat=True)

    plt.show()


def animate_plots_xy(plots, interval=35, xlim=None, ylim=None):

    fig, ax = plt.subplots()
    if xlim is not None:
        ax.set_xlim(xlim[0],xlim[1])
    if ylim is not None:
        ax.set_ylim(ylim[0],ylim[1])

    lines = []
    for p in plots[0]:
        for c in p:
            line, = ax.plot(c[0],c[1])
            lines += [line]

    def init():
        return lines

    def animate(i):
        p = plots[i]
        for line,c in zip(lines,p):
            line.set_xdata(c[0])  # update the data.
            line.set_ydata(c[1])  # update the data.
        return lines

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, interval=interval, blit=True,frames=len(plots),repeat=True)

    plt.show()


def show_images(imgs):
    for img in imgs:
        plt.figure()
        if np.max(img) > 1:
            img = data.normalize_01(img)
        if len(img.shape) == 2:
            plt.imshow(img,cmap='Greys')
        else:
            plt.imshow(img)
    plt.show()

def start_image_server(generate_image_function,color_string,seed):
    import utils.ui_utils.image_server as image_server
    image_server.start_server(generate_image_function,color_string,seed)