import numpy as np
from collections import namedtuple
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from utils.markov_utils import *
from properties import *

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 100
WIDTH  = 100
UPSCALE_FACTOR = 20
N = 100

IMAGE_DEPTH = CHANNELS_GRAY

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '0.png'

### END OF SCRIPT HEADER #################################################
##########################################################################


OFFSET = 0.01


### There differen markov chains working in tandem,
### one if for deciding the length, the other one is for deciding the type


vs = np.linspace(0,1,num=WIDTH//4)
vs = np.repeat(vs,repeats=5)
# vs = np.concatenate((vs,vs[-2::-1]))
px_1 = FuzzyProgression(
    values=vs,
    positive_shifts=1,negative_shifts=1,
    repeat_factor=2)


np.random.seed(100)
values = []
for i in range(5):
    mask = np.random.binomial(1,p=0.5,size=WIDTH//10)
    vs = ['0','1',]
    pattern = ''.join([ vs[i] for i in mask ])
    print(pattern)
    values += [
        SimplePattern(pattern=pattern,candidates=[0,1]) ]

black_white = RandomMarkovModel(
    values=values,
    child_lengths=[WIDTH*i for i in range(1,2)])
varied = SimpleProgression(
    values=[px_1],
    child_lengths = [WIDTH*i for i in range(10,15)])
parent = RandomMarkovModel(
    values=[varied,black_white],
    child_lengths=[1,2])




def gen_channel(seed):
    img = paint_linearly_markov_hierarchy(
        markov_tree=parent, width=WIDTH, height=HEIGHT, seed=seed)
    img = upscale_nearest(img,UPSCALE_FACTOR)
    return img.reshape(HEIGHT*UPSCALE_FACTOR,WIDTH*UPSCALE_FACTOR,1)


# animation = np.zeros((N,HEIGHT*UPSCALE_FACTOR,WIDTH*UPSCALE_FACTOR,3))
for i in range(N):
    s = i*10
    img_1 = gen_channel(s+1)
    img_2 = gen_channel(s+2)
    img_3 = gen_channel(s+3)
    img = np.concatenate((img_1,img_2,img_3),axis=2)
    export_image('markov_h_%d' % (i),img,'png')
    # export_image('markov_h_%d.png' % (i), img,'png',quality=100)
    # animation[i] = img
# export_animation('anim.gif',animation,loop=2)
