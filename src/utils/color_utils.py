import numpy as np
import colorsys
import colorspacious as cs

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# This is done to make sure that the colour library works only with values between 0 and 1
# colour.set_domain_range_scale('1')

def linspace_hue(start,end,num_steps):
    diff = start - end
    diff_1 = np.abs(diff) # this represents direct interpolation
    diff_2 = np.abs(diff - np.sign(diff)*360) # this represents going around the circle
    if diff_1 < diff_2:
        l = np.linspace(start, end, num_steps)
    else:
        l = np.linspace(start,end + np.sign(diff)*360,num_steps)

    l[l>=360] -= 360
    l[l<0] += 360
    return l



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


def srgb2cam02(rgb):
    return cs.cspace_convert(rgb, "sRGB255", "JCh")

def cam022srgb(cam02):
    return cs.cspace_convert(cam02, "JCh", "sRGB255")

def srgb2cam02ucs(rgb):
    return cs.cspace_convert(rgb, "sRGB255", cs.CAM02UCS)

def cam02ucs2srgb(cam02):
    return cs.cspace_convert(cam02, cs.CAM02UCS, "sRGB255")


def srgb2lab(rgb):
    return cs.cspace_convert(rgb,'sRGB255','CIELab')

def lab2srgb(lab):
    return cs.cspace_convert(lab,'CIELab','sRGB255')



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



def build_color_dictionary(s):
    return {
        key:(color,meta)
        for key,color,meta in parse_line_color_states(s)
    }


def build_list_color_dictionaries(s):
    return [
        build_color_dictionary(i)
        for i in s.split('|')
    ]

def parse_line_color_states(s):
    return [ parse_color_state(i) for i in s.split('-')  ]

def parse_color_state(s):
    ss = s.split('/')
    key = None
    meta = None
    color = None
    if len(ss[0]) > 0:
        key = int(ss[0])
    if len(ss[1]) > 0:
        color = ss[1]
    if len(ss[2]) > 0:
        meta = ss[2]
    return (key,color,meta)

def convert_color_dict_from_hex(color_dict):
    return {i:hex2rgb(j[0]) for i, j in color_dict.items()}

def replace_indices_with_colors(img, color_dict):


    color_dict = convert_color_dict_from_hex(color_dict)
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in color_dict.items():
        mask = img == key
        new_img[mask] = item

    return new_img.astype('uint8')
