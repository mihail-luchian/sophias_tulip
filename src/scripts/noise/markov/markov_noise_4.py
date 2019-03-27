import numpy as np
import constants as c
from utils.generate_utils import *
from utils.file_utils import *
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
N = 100

HEIGHT = 200
WIDTH  = HEIGHT
UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

NUM_GEN_PATTERNS = 15
PATTERN_LENGTH = 9
MAX_HEIGHT = 3



COLOR_DICT = {
    0: np.array([0,0,0]),
    1: np.array([255,255,255])
}

print(COLOR_DICT)

### FUNCTIONS section
def gen_channel(parent,seed):
    img = m.gen_img_markov_hierarchy(
        markov_tree=parent, width=WIDTH, height=HEIGHT)
    img = data.upscale_nearest(img,UPSCALE_FACTOR)
    return img.reshape(HEIGHT*UPSCALE_FACTOR,WIDTH*UPSCALE_FACTOR,1)


### GENERATE SECTION

for current_iteration in range(N):

    np.random.seed(4600+current_iteration)

    PATTERN_LENGTH = 10
    def stringify_pattern(first,second, others):
        s = [
            second if i in others else first
            for i in range(PATTERN_LENGTH)
        ]

        return ''.join(s)


    patterns_white = [
        stringify_pattern(
            '1','0',
            np.random.choice(
                PATTERN_LENGTH,
                size=np.random.choice(PATTERN_LENGTH//2-1)+1,
                replace=False))
        for i in range(30)
    ] + ['1'*PATTERN_LENGTH]
    # print('patterns white',patterns_white)


    patterns_black = [
        stringify_pattern(
            '0','1',
            np.random.choice(
                PATTERN_LENGTH,
                size=np.random.choice(PATTERN_LENGTH//2-1)+1,
                replace=False))
        for i in range(30)
    ] + ['0'*PATTERN_LENGTH]


    patterns_white =  [
        m.SimplePattern(pattern=i,candidates=[0,1]) for i in patterns_white ]

    patterns_black = [
        m.SimplePattern(pattern=i,candidates=[0,1]) for i in patterns_black ]


    row_patterns_white = [ m.SimpleProgression( values =
        m.RandomMarkovModel(values=patterns_white, child_lengths=[i]),
        child_lengths=j )
        for (i,j) in [ [50,4],[100,20],[200,1] ]
    ]

    row_patterns_white = m.RandomMarkovModel(
        values=row_patterns_white,child_lengths=5)

    row_patterns_black = [ m.SimpleProgression( values =
        m.RandomMarkovModel(values=patterns_black, child_lengths=[i]),
        child_lengths=j )
        for (i,j) in [ [50,4],[100,20],[200,1] ]
    ]

    row_patterns_black = m.RandomMarkovModel(
        values=row_patterns_black,child_lengths=5)

    whites = m.SimpleProgression(
        values= m.MarkovModel(
            values = [0,1],
            preference_matrix=[ [0,1],[1,25] ]),
        child_lengths=[WIDTH*i for i in range(4,6)])

    white_blocks = m.RandomMarkovModel(
        values = [whites,row_patterns_white],
        child_lengths=[5,6,7])


    blacks = m.SimpleProgression(
        values=m.MarkovModel(
            values=[0, 1],
            preference_matrix=[[25,1],[1,0]]),
        child_lengths=[WIDTH * i for i in range(4, 6)])

    black_blocks = m.RandomMarkovModel(
        values = [blacks,row_patterns_black],
        child_lengths=[5,6,7])

    parent = m.RandomMarkovModel(
        values=[white_blocks,black_blocks],child_lengths=1)

    s = current_iteration*10
    img = gen_channel(parent,s+1)[:,:,0]
    print(img.shape)
    colored_image = color.replace_indices_with_colors(img, COLOR_DICT)
    print(colored_image.shape)

    if N==1:
        viz.show_image(colored_image)
    else:
        export_image(
        'markov_h_%d' % (current_iteration),colored_image.astype('uint8'),format='png')
