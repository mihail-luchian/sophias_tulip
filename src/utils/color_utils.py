import numpy as np

def hex2arr(s):

    only_digits = s[-6:]
    if len(only_digits) == 6:
        r = only_digits[0:2]
        g = only_digits[2:4]
        b = only_digits[4:6]

        r = int(r, 16)
        g = int(g, 16)
        b = int(b, 16)
    else:
        r = 0
        g = 0
        b = 0

    return np.array([r, g, b])

def convert_color_dict_from_hex(color_dict):
    return { i:hex2arr(j) for i,j in color_dict.items() }

def replace_indices_with_colors(img, color_dict):


    color_dict = convert_color_dict_from_hex(color_dict)
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in color_dict.items():
        mask = img == key
        new_img[mask] = item

    return new_img
