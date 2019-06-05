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
N = 1
SEED = config.get('seed',0)
HEIGHT = 100
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT
NUM_COLORS = 10
UPSCALE_COLORS = HEIGHT // (NUM_COLORS*2)


STRING_COLORS_1 = config.get(
    'colors_1','aaaaaa-aaaaaa-aaaaaa-aaaaaa-aaaaaa')
STRING_COLORS_2 = config.get(
    'colors_2','aaaaaa-aaaaaa-aaaaaa-aaaaaa-aaaaaa')

COLOR_DICT_1 = {
    i:j
    for i,j in enumerate(STRING_COLORS_1.split('-'))
}


COLOR_DICT_2 = {
    10+i:j
    for i,j in enumerate(STRING_COLORS_2.split('-'))
}

COLOR_DICT = {
    **COLOR_DICT_1,
    **COLOR_DICT_2,
}


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


def gen_img_from_accumulations_blueprint(acums, colors, color_dict):

    color_dict_hex = {
        i:color.hex_2_hsv(j)
        for i,j in color_dict.items()
    }

    start_color_indices = colors[0,:]
    end_color_indices = colors[1,:]

    start_colors = np.array( [color_dict_hex[i] for i in start_color_indices] )
    end_colors = np.array( [color_dict_hex[i] for i in end_color_indices] )

    hue_distance = end_colors[:,0] - start_colors[:,0]
    sat_distance = end_colors[:,1] - start_colors[:,1]
    value_distance = end_colors[:,2] - start_colors[:,2]

    img_height,img_width = acums.shape
    default_color = np.ones((img_height,img_width,3)) *  start_colors[:,np.newaxis,:]
    # num_steps = np.mean(np.abs(acums[acums>np.mean(acums)*1.5]))
    num_steps = np.abs(np.max(acums,axis=1))
    print('NUM_STEPS',num_steps)
    layer_hue = acums*(hue_distance/num_steps)[:,np.newaxis] + default_color[:, :, 0]
    layer_saturation = default_color[:, :, 1] + acums*(sat_distance/num_steps)[:,np.newaxis]
    layer_value = default_color[:, :, 2] + acums*(value_distance/num_steps)[:,np.newaxis]

    final = np.stack((layer_hue, layer_saturation, layer_value), axis=2)
    final = color.clamp_hsv_opencv(final)
    final = cv2.cvtColor(final,cv2.COLOR_HSV2RGB)*255

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)


    # GENERATING THE COLORS FIRST

    length_choices = [1,2]
    lengths_1 = r.choice(length_choices,size=5)
    lengths_2 = r.choice(length_choices,size=5)

    color_row_1 = m.Processor(
        m.RMM(values=[0,1,2,3,4],self_length=WIDTH,lenghts=lengths_1),
        length_limit=WIDTH)
    color_row_2 = m.Processor(
        m.RMM(values=[10, 11, 12, 13, 14], self_length=WIDTH, lenghts=lengths_2),
        length_limit=WIDTH)
    color_parent = m.SProg(values=[color_row_1, color_row_2], start_probs=0)
    colors = gen_portion(color_parent,2,WIDTH)

    print(colors[:,:30])

    skips = [-1,1, -2,2, -3,3, -4,4, -5,5, 0]

    base_pattern = config.get('pattern_base',[0,1,0,1,0,1,0,1,0,1])

    patterns = [

        config.get('pattern_1', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_2', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_3', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
        config.get('pattern_4', [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    ]

    print(patterns)

    base_pattern = to_string_pattern(base_pattern,skips)
    patterns = [
        to_string_pattern(i,skips)
        for i in patterns
    ]

    print(patterns)

    base_pattern = m.SimplePattern(
        pattern=base_pattern,
        candidates=skips,
        start_probs=[0,1,2,3],
        self_length=[WIDTH//10,WIDTH//10-1,2*WIDTH//10,2*WIDTH//10-1,3*WIDTH//10,3*WIDTH//10-1])
    base_pattern = m.Proc(
        m.SProg(values=base_pattern, self_length=25),
        num_tiles=[3],length_limit=WIDTH)

    patterns = [
        m.SPat(pattern=p, candidates=skips, start_probs=[0, 1])
        for p in patterns
    ]

    child_lengths = [2*WIDTH//10,3*WIDTH//10,4*WIDTH//10]
    patterns = m.Proc(
                m.RMM(values=patterns,child_lengths=child_lengths,self_length=15),
                length_limit=WIDTH, num_tiles=[2,3])

    patterns = m.SProg(values=patterns, self_length=[1, 2, 3])

    parent = m.RMM(values=[base_pattern,patterns])

    img = gen_portion(parent, HEIGHT, WIDTH)
    print(img)
    img_acum = np.cumsum(img,axis=1)
    img_acum = data.upscale_nearest(img_acum,UPSCALE_FACTOR)
    colors = data.upscale_nearest(colors,ny=1,nx=UPSCALE_FACTOR)

    if N==1:
        viz.start_color_editing_tool(
            blueprint=img_acum,
            color_dict=COLOR_DICT,
            downsample=2,
            gen_fun = lambda x,y: gen_img_from_accumulations_blueprint(x,colors[:,::2],y) )
    else:
        final_img = gen_img_from_accumulations_blueprint(img_acum,colors,COLOR_DICT)
        file.export_image(
            '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
            final_img.astype('uint8'),format='png')
