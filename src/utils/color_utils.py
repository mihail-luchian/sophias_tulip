import numpy as np

def hex2arr(s):

    only_digits = s[-6:]
    r = only_digits[0:2]
    g = only_digits[2:4]
    b = only_digits[4:6]

    r = int(r, 16)
    g = int(g, 16)
    b = int(b, 16)

    return np.array([r, g, b])

def replace_indices_with_colors(img,dict_colors):
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in dict_colors.items():
        mask = img == key
        new_img[mask] = item

    return new_img
