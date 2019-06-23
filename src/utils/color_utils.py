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



def hex_2_rgb(s):

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


def srgb_2_cam02(rgb):
    return cs.cspace_convert(rgb, "sRGB255", "JCh")

def cam02_2_srgb(cam02):
    return cs.cspace_convert(cam02, "JCh", "sRGB255")

def srgb_2_cam02ucs(rgb):
    return cs.cspace_convert(rgb, "sRGB255", cs.CAM02UCS)

def cam02ucs_2_srgb(cam02):
    return cs.cspace_convert(cam02, cs.CAM02UCS, "sRGB255")


def srgb_2_lab(rgb):
    return cs.cspace_convert(rgb,'sRGB255','CIELab')

def lab_2_srgb(lab):
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

def hex_2_hsv(s):
    r,g,b = hex_2_rgb(s)
    return np.array(colorsys.rgb_to_hsv(r,g,b))*[255,255,1]

def interpolate_hex_colors(start,end,n):
    r1,g1,b1 = hex_2_rgb(start)
    r2,g2,b2 = hex_2_rgb(end)

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



def build_palette_from_state(s):
    return {
        key:(color,meta)
        for key,color,meta in parse_palette(s)
    }


def build_list_palettes(s):
    return [
        build_palette_from_state(i)
        for i in s.split(',')
    ]


def build_color_repository(s):


    return {
        s1: build_palette_from_state(s2)
        for i in s.split(',')
        for s1,s2 in [i.split(':')]
    }


def get_keys_from_palette(palette):
    return [i for i in palette.keys()]

def get_colors_from_palette(palette,keys=None):
    if keys is None:
        return [j for i,(j,_) in palette.items()]
    else:
        return [palette[key][0] for key in keys]


def palette_2_color_dict(palette):
    return {i:j for i,(j,_) in palette.items()}


def get_meta_from_palette(palette,keys=None,meta_cast_function=None):

    if keys is None:
        meta = [j for i,(_,j) in palette.items()]
    else:
        meta = [palette[key][1] for key in keys]

    if meta_cast_function is None:
        return meta
    else:
        return [ meta_cast_function(i) for i in meta]


def flatten_list_palettes(list_color_palettes):
    return {
        i:j
        for d in list_color_palettes
        for i,j in d.items()
    }


def flatten_dict_palettes(dict_color_palettes):
    return {
        i:j
        for _,d in dict_color_palettes.items()
        for i,j in d.items()
    }

def parse_palette(s):
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


def hex_palette_2_rgb_palette(color_dict):
    return {i:hex_2_rgb(j) for i, (j, _) in color_dict.items()}

def replace_indices_with_colors(img, hex_palette):

    hex_palette = hex_palette_2_rgb_palette(hex_palette)
    new_img = np.zeros(list(img.shape)+[3])
    for key,item in hex_palette.items():
        mask = img == key
        new_img[mask] = item

    return new_img.astype('uint8')
