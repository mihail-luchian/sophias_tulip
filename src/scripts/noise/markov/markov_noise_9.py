print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import cv2
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 30
SEED = config.get('seed',0)
HEIGHT = 500
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


STRING_COLORS = config.get(
    'colors','aaaaaa-aaaaaa-aaaaaa-aaaaaa-aaaaaa')

COLOR_DICT = {
    i:j
    for i,j in enumerate(STRING_COLORS.split('-'))
}

COLOR_DICT = {
    **COLOR_DICT,
}


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


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



def generate_color_image(acums, colors_acum, color_dict):

    color_dict_cam = {
        i: color.srgb_2_cam02ucs(color.hex_2_rgb(j))
        for i,j in color_dict.items()
    }

    # solving first the vertical gradients
    color_column_left_start  = color_dict_cam[0]
    color_column_left_end    = color_dict_cam[1]
    color_column_right_start = color_dict_cam[2]
    color_column_right_end   = color_dict_cam[3]

    column_left_acum = colors_acum[0]
    column_right_acum = colors_acum[1]

    column_left_diff = (color_column_left_end - color_column_left_start)/np.max(np.abs(column_left_acum))
    column_right_diff = (color_column_right_end - color_column_right_start)/np.max(np.abs(column_right_acum))

    print('COL_LEFT ACUM MAX',np.max(np.abs(column_left_acum)))
    print('COL_RIGHT ACUM MAX',np.max(np.abs(column_right_acum)))

    column_left = color_column_left_start + column_left_acum[:,np.newaxis]*column_left_diff
    column_right = color_column_right_start + column_right_acum[:,np.newaxis]*column_right_diff

    # print(column_left_acum)

    # solving the overal gradients
    j_distance   = column_right[:,0] - column_left[:,0]
    c_distance   = column_right[:,1] - column_left[:,1]
    h_distance = column_right[:,2] - column_left[:,2]

    img_height,img_width = acums.shape
    default_color = np.ones((img_height,img_width,3)) *  column_left[:,np.newaxis,:]
    num_steps = np.abs(np.max(acums,axis=1))
    layer_j = acums*(j_distance/num_steps)[:,np.newaxis] + default_color[:, :, 0]
    layer_c = default_color[:, :, 1] + acums*(c_distance/num_steps)[:,np.newaxis]
    layer_h = default_color[:, :, 2] + acums*(h_distance/num_steps)[:,np.newaxis]

    final = np.stack((layer_j, layer_c, layer_h), axis=2)
    final = color.cam02ucs_2_srgb(final)
    final = np.clip(final,0,255)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)

    skips = config.get('skips',[-1,1, -2,2, -3,3, -4,4, -5,5, 0])

    color_patterns_1 = [
        config.get('pattern_color_1_a', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_color_1_b', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_color_1_c', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    ]
    color_patterns_2 = [
        config.get('pattern_color_2_a', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    ]

    color_patterns_1 = [to_string_pattern(i, skips) for i in color_patterns_1]
    color_patterns_2 = [to_string_pattern(i, skips) for i in color_patterns_2]

    patterns_1 = [
        config.get('pattern_1_a', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_1_b', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_1_c', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_1_d', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_1_e', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    ]
    patterns_2 = [
        config.get('pattern_2_a', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    ]
    patterns_1 = [to_string_pattern(i, skips) for i in patterns_1]
    patterns_2 = [to_string_pattern(i, skips) for i in patterns_2]

    # generating the color columns
    color_patterns = [
        m.SPat(pattern=p, self_length=len(p), candidates=skips,lenghts=r.choice([1,2,3,4]))
        for p in color_patterns_1
        for i in range(5)
    ]
    color_patterns += [
        m.SPat(pattern=p, self_length=len(p), candidates=skips,lenghts=r.choice([5,10,14,15]))
        for p in color_patterns_2
        for i in range(2)
    ]


    color_column_left = m.Proc(
        m.SProg(values=color_patterns, self_length=WIDTH // 3), length_limit=WIDTH)

    color_column_right = m.Proc(
        m.SProg(values=color_patterns, self_length=WIDTH // 3), length_limit=WIDTH)
    color_parent = m.SProg(values=[color_column_left, color_column_right],start_probs=0)

    colors_deriv = m.paint_linearly_markov_hierarchy(
        markov_tree=color_parent, width=WIDTH, height=2)
    colors_acum = np.cumsum(colors_deriv, axis=1)


    # generating the row transitions
    patterns = [
        m.SPat(pattern=p,candidates=skips,start_probs=[0,1],lenghts=r.choice([1,2,3,4,5]),self_length=len(p))
        for p in patterns_1
        for _ in range(3)
    ]
    patterns += [
        m.SPat(pattern=p,candidates=skips,start_probs=[0,1],lenghts=r.choice([5,10,15]*2+[30,40,50,60]),self_length=len(p))
        for p in patterns_2
        for _ in range(3)
    ]

    line = m.Proc(
        m.RMM(values=patterns, self_length=WIDTH),
        length_limit=[WIDTH,WIDTH//2,WIDTH-1],num_tiles=[1,3,4,5] + [20,30,40])

    multi_lines = m.Proc(
        m.SProg(values=line,self_length=50),length_limit=[i*WIDTH for i in range(100,150)],num_tiles=[1,2])
    parent = m.SProg(values=multi_lines)

    img_deriv = m.paint_linearly_markov_hierarchy(
        markov_tree=parent, width=WIDTH, height=HEIGHT)
    img_acum = np.cumsum(img_deriv, axis=1)
    img_acum = data.upscale_nearest(img_acum,UPSCALE_FACTOR)
    colors_acum = data.upscale_nearest(colors_acum, ny=1, nx=UPSCALE_FACTOR)


    if N==1:
        viz.start_color_editing_tool(
            blueprint=img_acum,
            color_dict=COLOR_DICT,
            downsample=2,
            gen_fun = lambda x, color_dict: generate_color_image(x, colors_acum[:, ::2], color_dict) )
    else:
        final_img = generate_color_image(img_acum, colors_acum, COLOR_DICT)
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            final_img.astype('uint8'),format='png')