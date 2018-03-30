import numpy as np


def generate_horizontal_gradient(shape, start, end, gamma_correction = True, gamma = 2.2):
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