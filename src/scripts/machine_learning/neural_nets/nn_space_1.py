print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.nn_utils as nn
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt
import tensorflow as tf

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')

DUMP_PREVIOUS_EXPORTS = False
SHOW_DEBUG_DATA = False
START_SERVER = False
SHOW_IMAGES = True
SAVE_IMAGES = False

N = 1
SEED = config.get('seed',325)
HEIGHT = 500
WIDTH  = 500

INPUT_SIZE = 2

COLOR_STRING = config.get(
    'color-string',
    'First:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2,Second:0/84ffd4/-1/39f9ed/-2/1ddbf4/-3/1168f4/-4/1da4f2/,Third:0/fff2c9/2-1/f3ff75/3-2/a7fc4b/3-3/a0ffa8/3-4/d6ffdc/2')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_folder()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def build_network(input,rgen):

    input = tf.reshape(input,shape=[-1,INPUT_SIZE*INPUT_SIZE])
    # print(input.get_shape().as_list())

    wdev = 0.5
    bdev = 0.5

    dense = nn.dense_layer(
        input,32,activation=tf.nn.tanh,
        wdev=wdev,bdev=bdev,
        rgen=r.bind_generator_from(rgen),
    )

    for i in range(8):
        dense = nn.dense_layer(
            dense,32,activation=tf.nn.tanh,
            wdev=wdev,bdev=bdev,
            rgen=r.bind_generator_from(rgen),
        )


    dense = nn.dense_layer(
        dense,3,
        wdev=wdev,bdev=bdev,
        rgen=r.bind_generator_from(rgen),
        activation=tf.nn.tanh)

    return dense


def generate_full_image(color_string,seed):
    r.init_def_generator(seed)
    rgen = r.bind_generator()

    input = tf.placeholder('float32',shape=[None,INPUT_SIZE,INPUT_SIZE])
    network = build_network(input=input,rgen=r.bind_generator_from(rgen))

    print(network.get_shape())

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)

        scale = 2
        ly1 = np.linspace(-1*scale,1*scale,num=HEIGHT)
        ly2 = np.linspace(1*scale,-1*scale,num=HEIGHT)
        lx1 = np.linspace(-1*scale,1*scale,num=WIDTH)
        lx2 = np.linspace(1*scale,-1*scale,num=WIDTH)

        yy1,xx1 = np.meshgrid(ly1,lx1)
        yy2,xx2 = np.meshgrid(ly2,lx2)

        f = np.c_[
            yy1.flatten(),
            xx1.flatten(),
            yy2.flatten(),
            xx2.flatten()
        ]
        f = f.reshape([-1,2,2])

        output, = sess.run([network],{input:f})

    print(output.shape)
    image = output.reshape([HEIGHT,WIDTH,3])
    print(np.max(image),np.min(image))
    image = np.clip(image,-1,1)/2 + 0.5
    return image


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)

    if START_SERVER is True:
        viz.start_image_server(
            generate_full_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    else:
        image = generate_full_image(COLOR_STRING,SEED+current_iteration)
        if SAVE_IMAGES is True:
            print('\tSAVING IMAGE')
            file.export_image(
                '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
                image.astype('uint8'),format='png')
        elif SHOW_IMAGES is True:
            viz.show_image(image)


