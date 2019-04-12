print('IMPORTING MODULES')
import time
import constants as c
import numpy as np
import cv2
import utils.generate_utils as gen
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 30
SEED = 0
HEIGHT = 100
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

COLOR_DICT = {0: '6eb9e1', 1: '032b5b'}


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def gen_portion(parent,height,width,tile_height=None,tile_width=None):
    img = m.paint_linearly_markov_hierarchy(
        markov_tree=parent,
        width=width, height=height,tile_width=tile_width,tile_height=tile_height)
    return img.reshape(img.shape[0],img.shape[1])



def to_string_pattern(p,values):
    dictionary_pos = {
        values[i]:i
        for i in range(len(values))
    }

    poss = [
        dictionary_pos[i]
        for i in p
    ]

    return ''.join(c.PATTERN_INDICES_STR[i] for i in poss)


def gen_img_from_accumulations_blueprint(acums, color_dict):

    start_color = color.hex2hsv(color_dict[0])
    end_color = color.hex2hsv(color_dict[1])

    hue_distance = end_color[0] - start_color[0]
    sat_distance = end_color[1] - start_color[1]
    value_distance = end_color[2] - start_color[2]

    img_height,img_width = acums.shape
    default_color = np.ones((img_height,img_width,3)) *  start_color

    num_steps = 30
    layer_hue = acums*(hue_distance/num_steps) + default_color[:, :, 0]
    layer_saturation = default_color[:, :, 1] + acums*(sat_distance/num_steps)
    layer_value = default_color[:, :, 2] + acums*(value_distance/num_steps)

    final = np.stack((layer_hue, layer_saturation, layer_value), axis=2)
    final = color.clamp_hsv_opencv(final)
    final = cv2.cvtColor(final,cv2.COLOR_HSV2RGB)*255

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    np.random.seed(SEED+current_iteration)

    skips = [-1,1, -2,2, -3,3, -4,4, -5,5, 0]

    base_pattern = [
            4,-2,
            -2,2,
            -3,3,
            -4,4,
            -3,3
        ]

    patterns = [

        [
            -3, 0,
            5, 0,
            -3, 0,
            5, 0,
            -2, 0,
        ], # sum -> 2

        [
            -3, 0,
            4, 0,
            -2, 0,
            4, 0,
            -2, 0,
        ], # sum -> 1
        [
            -3, 2, 2,
            -3, 2, 2,
            -3, 2, 2,
            0,
        ], # sum -> 3
        [
            -4, 3, 2,
            -4, 3, 2,
            -4, 3, 2,
            0,
        ], # sum -> 3
        [
            -2, 2, 1,
            -2, 2, 1,
            -2, 2, 1,
            0,
        ], # sum -> 3
    ]



    base_pattern = to_string_pattern(base_pattern,skips)
    patterns = [
        to_string_pattern(i,skips)
        for i in patterns
    ]

    print(patterns)

    base_pattern = m.SimplePattern(
        pattern=base_pattern,
        candidates=skips,
        start_probs=[0,1,2],
        self_length=[2*WIDTH//10,2*WIDTH//10-1,3*WIDTH//10,3*WIDTH//10-1])
    base_pattern = m.Prcs(
        m.SPr(values=base_pattern,self_length=15),
        num_tiles=[3,6],length_limit=WIDTH)

    patterns = [
        m.SPt(pattern=p,candidates=skips,start_probs=[0,1])
        for p in patterns
    ]

    child_lengths = [2*WIDTH//10,3*WIDTH//10,4*WIDTH//10]
    patterns = m.Prcs(
                m.RMM(values=patterns,child_lengths=child_lengths,self_length=10),
                length_limit=WIDTH, num_tiles=[1,2,3])

    patterns = m.SPr(values=patterns,self_length=[1,2,3])

    parent = m.RMM(values=[base_pattern,patterns])
    # parent = m.RMM(values=[patterns])

    img = gen_portion(parent,HEIGHT,WIDTH)

    img_acum = np.cumsum(img,axis=1)
    img_acum = data.upscale_nearest(img_acum,UPSCALE_FACTOR)


    final = gen_img_from_accumulations_blueprint(img_acum, COLOR_DICT)

    if N==1:
        viz.start_color_editing_tool(
            blueprint=img_acum,
            color_dict=COLOR_DICT,
            downsample=2,
            gen_fun = gen_img_from_accumulations_blueprint)
    else:
        final_img = gen_img_from_accumulations_blueprint(img_acum,COLOR_DICT)
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            final_img.astype('uint8'),format='png')
