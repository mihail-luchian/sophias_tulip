import matplotlib.pyplot as plt
import matplotlib.animation as animation

def show_animation(data):
    fig = plt.figure()
    ims = []
    for d in data:
        im = plt.imshow(d, animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(
        fig, ims, interval=35, blit=True)

    plt.show()

def show_image(img):
    plt.imshow(img)
    plt.show()