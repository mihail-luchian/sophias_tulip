import numpy as np
import skimage.draw as draw


def horizontal_gradient(shape, start, end, gamma_correction = True, gamma = 2.2):
    '''

    :param shape: specifies the shape of the gradient, which might be 2d or 3d
                  shape[0] -> number of lines [y coordinate]
                  shape[1] -> number of columns [x coordinate]
                  shape[2] -> if present, number of channels
    :param start: the value with which to start the gradient
    :param end: the value with which to end the gradient
    :param gamma_correction: use game_correction on the gradient

    :return: returns a horizontal gradient
    '''

    y = shape[0]
    x = shape[1]
    gradient_base = np.linspace(0,1,x)

    if gamma_correction is True:
        gradient_base = np.power(gradient_base, gamma)

    gradient_base *= (end-start)
    gradient_base += start

    if len(shape)==3:
        gradient_base = np.repeat(gradient_base,shape[2])



    gradient = np.tile(gradient_base,y).reshape(shape)
    return gradient


def circle(size,rad = None,pos=None):

    height,width = size
    min_axis = min(height,width)
    if pos==None:
        pos_x = pos_y = min_axis//2+(min_axis%2-1)/2
    elif isinstance(pos, tuple):
        pos_x,pos_y = tuple
    else:
        pos_x = pos_y = pos
    if rad == None:
        rad = min_axis//2
        rad += (min_axis%2)/2

    img = np.zeros(size, dtype=np.uint8)
    rr, cc = draw.circle(pos_x, pos_y, rad)
    img[rr, cc] = 1

    return img

# possible useful patterns, write functions for them:
# Round windowing function
# box function
# circles

def line(size,start_pos=None,end_pos=None):
    img = np.zeros(size, dtype=np.float32)


    # we have to change the pos of x and y
    rr, cc = draw.line(start_pos[1], start_pos[0],end_pos[1], end_pos[0])
    img[rr, cc] = 1

    return img

def random_cross_line(size,seed=101,horizontal=True):
    np.random.seed(seed)

    height,width = size

    if horizontal == True:
        xs = (0,width-1)
        ys = np.random.choice(np.arange(height), size=(2,))
    elif horizontal == False:
        xs = np.random.choice(np.arange(height), size=(2,))
        ys = (0,height-1)

    return line( size, start_pos=(xs[0],ys[0]),end_pos=(xs[1],ys[1]) )


