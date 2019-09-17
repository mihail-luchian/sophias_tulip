import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *
import matplotlib.pyplot as plt

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 500
WIDTH  = 500

NOISE_NODES_Y = 20
NOISE_NODES_X = 20

BLOOM_MIN = 0.1
BLOOM_MAX = 1

IMAGE_DEPTH = CHANNELS_GRAY
# CHANNELS_GRAY
# TODO implement CHANNELS_3 image depth
# CHANNELS_3

RANDOM_SEED = 0

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '0.png'

### END OF SCRIPT HEADER #################################################
##########################################################################

np.random.seed(RANDOM_SEED)

def fade(t):
    # return 1 / (1 + np.exp(-t*10+5))
    return 6 * t**5 - 15 * t**4 + 10 * t**3

def exp_fade(grid_x,grid_y,cx,cy,spread):
    return np.exp( -((grid_x-cx)**2 + (grid_y-cy)**2)/spread )

RATIO_Y = HEIGHT // NOISE_NODES_Y
RATIO_X = WIDTH // NOISE_NODES_X
coords_y = np.linspace(0,NOISE_NODES_Y,HEIGHT,endpoint=False)
coords_x = np.linspace(0,NOISE_NODES_X,WIDTH,endpoint=False)
noise_index_y = coords_y.astype('int32')
noise_index_x = coords_x.astype('int32')
grid_x,grid_y = np.meshgrid(coords_x,coords_y)
grid_noise_index_x,grid_noise_index_y = np.meshgrid(noise_index_x,noise_index_y)
grid_dif_y = grid_y - grid_noise_index_y
grid_dif_x = grid_x - grid_noise_index_x

DATA_RANDOM_SHAPE = (NOISE_NODES_Y + 1, NOISE_NODES_X + 1)
data_theta_random = np.random.uniform(low=-np.pi, high=np.pi, size=DATA_RANDOM_SHAPE)
data_random = np.stack((np.cos(data_theta_random),np.sin(data_theta_random)),axis=2)

# data_switch = np.random.binomial(1,p=0.1,size=DATA_RANDOM_SHAPE)
# data_random[data_switch==0] *= 0
# data_switch = np.random.uniform(0,1,size=DATA_RANDOM_SHAPE)
# data_random = data_random * data_switch[:,:,None]
data_random_spread = np.random.uniform(BLOOM_MIN,BLOOM_MAX,size=DATA_RANDOM_SHAPE)
data_random_freq = np.random.uniform(1,5,size=DATA_RANDOM_SHAPE)

f = np.ones((HEIGHT,WIDTH))*0.5
for i in range(NOISE_NODES_Y+1):
    for j in range(NOISE_NODES_X+1):
        ty = grid_y - i
        tx = grid_x - j

        tf = ty*data_random[i,j,0] + tx*data_random[i,j,1]
        tf = np.sin(data_random_freq[i,j]*tf)
        tf = tf*exp_fade(grid_x,grid_y,cx=j,cy=i,spread=data_random_spread[i,j])
        f += tf


f = normalize_01(f)
print(f.shape)
export_image(EXPORT_NAME,f)
