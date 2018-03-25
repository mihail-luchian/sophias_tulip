import numpy as np

def shuffle_image_with_indices(img,indices):
    '''

    :param img: is a 3 dimensional tensor  [Y lines][X lines][3]
    :param indices: is a 4 dimensional tensor. [Y lines][X lines][3][3] or [Y lines][X lines][2]
           The interpretation is as following:
                1st case: for each value in each channel we have a coordinate from a different channel
                2nd case: for each pixel we have a new pixel coordinate
    :return: the reshuffled image
    '''

    last_dim = indices.shape[-1]
    indices_flatten = indices.astype('int32').reshape((-1,last_dim))
    if last_dim == 3:
        r = img[ indices_flatten[:,0],indices_flatten[:,1],indices_flatten[:,2] ]
    elif last_dim == 2:
        print(indices_flatten[:,0].shape)
        r = img[ indices_flatten[:,0],indices_flatten[:,1] ]
    print(r.shape)
    return r.reshape( img.shape )


