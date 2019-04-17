import numpy as np
import colorsys

def hex2rgb(s):

    only_digits = s[-6:]
    if len(only_digits) == 6:
        r = only_digits[0:2]
        g = only_digits[2:4]
        b = only_digits[4:6]

        try:
            r = int(r, 16)
            g = int(g, 16)
            b = int(b, 16)
        except ValueError:
            r = g = b = 0

    else:
        r = g = b = 0

    return np.array([r, g, b])

def clamp_hsv_opencv(a):

    lr_hue = (a[:,:,0]/255)*360
    lr_sat = a[:,:,1]/255
    lr_val = a[:,:,2]/255

    lr_hue[lr_hue>360] -= 360
    lr_hue[lr_hue<0] += 360

    lr_sat[lr_sat<0] = 0
    lr_sat[lr_sat>1] = 1

    lr_val[lr_val<0] = 0
    lr_val[lr_val>1] = 1

    return np.concatenate(
        (lr_hue[:,:,np.newaxis],lr_sat[:,:,np.newaxis],lr_val[:,:,np.newaxis]), axis=2).astype('float32')

def hex2hsv(s):
    r,g,b = hex2rgb(s)
    return np.array(colorsys.rgb_to_hsv(r,g,b))*[255,255,1]

def interpolate_hex_colors(start,end,n):
    r1,g1,b1 = hex2rgb(start)
    r2,g2,b2 = hex2rgb(end)

    def hs(x):
        s = hex(x)[2:]
        if len(s) > 1:
            return s
        else:
            return '0'+s

    r_interp = np.linspace(r1,r2,n).astype('uint8')
    g_interp = np.linspace(g1,g2,n).astype('uint8')
    b_interp = np.linspace(b1,b2,n).astype('uint8')

    return {
        i : hs(r_interp[i]) + hs(g_interp[i]) + hs(b_interp[i])
        for i in range(n)
    }



def convert_color_dict_from_hex(color_dict):
    return {i:hex2rgb(j) for i, j in color_dict.items()}

def replace_indices_with_colors(img, color_dict):


    color_dict = convert_color_dict_from_hex(color_dict)
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in color_dict.items():
        mask = img == key
        new_img[mask] = item

    return new_img.astype('uint8')
