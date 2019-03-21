import constants as C
import numpy as np
from utils.file_utils import *
from properties import *
import tensorflow as tf
import utils.nn_utils as nn
import utils.data_utils as data
import utils.viz_utils as viz
import utils.markov_utils as markov
import utils.generate_utils as gen
import matplotlib.pyplot as plt
import matplotlib.animation as animation


##########################################################################
### SCRIPT HEADER ########################################################

RUN_MODE = TRAIN

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NN_NAME = 'fit_image'

### END OF SCRIPT HEADER #################################################
##########################################################################

image_bottom = load_keukenhof_low()
print(image_bottom.shape)
part = image_bottom[:121,:121,0]


def make_deconvolution_layer(
        input, filter_shape, output_shape,
        name='var', dev=0.1, seed=10, filter=None, activation=True):

    if filter is None:
        filter = nn.create_variable(filter_shape, name, dev=dev, seed=seed)
    bias = nn.create_variable(output_shape,name=name+'_bias',dev=dev,seed=seed)
    h = tf.nn.conv2d_transpose(
        input, filter,
        strides=[1, 2, 2, 1],
        output_shape=output_shape,
        padding='SAME',
        data_format='NHWC')
    # h = h+bias/500
    if activation is True:
        h = tf.nn.relu(h)
        # h = tf.math.log1p(h)
        # h = tf.math.sin(h)

    return h



def generator(z):
    with tf.variable_scope("Generator"):

        last_layer_size = 7
        prev_layer_depth = 8
        offset = 100


        mask = gen.circle((last_layer_size,last_layer_size))
        cool_filter = np.random.normal(
            0,1,size=[last_layer_size,last_layer_size,1,prev_layer_depth]).astype('float32')
        for i in range(prev_layer_depth):
            start = offset + i*50
            end_1 = start + last_layer_size
            end_2 = start + prev_layer_depth
            patch = (image_bottom[start:end_1,start:end_1,0]).astype('float32')
            patch = np.sin(patch)
            patch -= np.mean(patch)
            cool_filter[:,:,0,i] = patch
            viz.show_image(patch)
        cool_filter = data.normalize_tensor(cool_filter)


        lines_size = 25
        lines_prev = 6
        r = np.random.binomial(1,0.5, size=(prev_layer_depth*lines_prev)).astype('bool')
        lines = np.array(
            [
                data.normalize_tensor(
                    gen.random_cross_line((lines_size,lines_size), seed=i*20+1, horizontal=r[i])*0.2
                    +
                    gen.random_cross_line((lines_size,lines_size), seed=i*30+1, horizontal=r[i])*0.5
                    -
                    gen.random_cross_line((lines_size,lines_size), seed=i*40+1, horizontal=r[i])*0.2
                    -
                    gen.random_cross_line((lines_size,lines_size), seed=i*50+1, horizontal=r[i])*0.5,
                    use_negative=True)
                for i in range(prev_layer_depth*lines_prev)]).astype('float32')

        lines = np.reshape(lines,(lines_size,lines_size,prev_layer_depth,lines_prev))

        names = ['f1','f2','f3','f4','f5']
        szs = [3,3,lines_size,last_layer_size]
        depths = [2,lines_prev,prev_layer_depth,1]
        fs = [None,None,lines,cool_filter]
        activations = [True,True,True,False]
        max_pool = [False,True,False,True]
        prev_depth = 1
        h = z
        current_width = int(z.shape[1])
        print(current_width)
        for i,(name,size,depth,f,acts,mp) in enumerate(
                zip(names,szs,depths,fs,activations,max_pool)):
            current_width += current_width
            h = make_deconvolution_layer(
                h,[size,size,depth,prev_depth],
                [1,current_width,current_width,depth],
                name,dev=0.1,seed = i*50+3,filter=f,activation=acts)
            if mp is True:
                h = tf.nn.max_pool(h,ksize=(1,2,2,1),strides=[1,2,2,1],padding='VALID')
                current_width = current_width // 2
            h -= tf.math.reduce_mean(h)

            prev_depth = depth


        out = h
        # print(out)
        # out = tf.nn.max_pool(out,ksize=(1,2,2,1),strides=[1,2,2,1],padding='VALID')
        # print(out)

        # conv_name = 'conv'
        # filter = nn.create_variable([3,3,1,1], conv_name, dev=0.01, seed=100)
        # bias = nn.create_variable([1,],name=conv_name+'_bias',dev=0.01, seed=100)
        # out = tf.nn.conv2d(
        #     out, filter,
        #     strides=[1, 2, 2, 1],
        #     padding='VALID',
        #     data_format='NHWC')
        # out = out+bias
        #
        # print(out)

        return out


z = tf.placeholder('float32',shape=[1,25,25,1])
out = generator(z)
print(out.get_shape())
print(tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES))



def gen_coherent_noise(height,width):

    vs = np.linspace(-0.2, 0.2, num=width)
    px_1 = markov.FuzzyProgression(
        values=vs,
        positive_shifts=3, negative_shifts=3,
        repeat_factor=4)

    np.random.seed(120)
    values = []
    for i in range(3):
        mask = np.random.binomial(1, p=0.5, size=width // 10)
        vs = ['0', '1','2' ]
        pattern = ''.join([vs[i] for i in mask])
        print(pattern)
        values += [
            markov.SimplePattern(pattern=pattern, candidates=[-0.5,0,0.5])]

    black_white = markov.RandomMarkovModel(
        values=values,
        child_lengths=[width * i for i in range(1, 2)])
    varied = markov.SimpleProgression(
        values=[px_1],
        child_lengths=[width * i for i in range(10, 15)])
    parent = markov.RandomMarkovModel(
        values=[varied, black_white],
        child_lengths=[1, 2])

    img = markov.gen_img_markov_hierarchy(
        markov_tree=parent, width=width, height=height, seed=20)

    return img

init = tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    np.random.seed(33)

    f = gen_coherent_noise(25,25)
    f = f.reshape(1,25,25,1)

    output, = sess.run([out],{z:f})
    print(output.shape)

    # viz.show_animation(output[0,:,:,i] for i in range(output.shape[-1]))
    for i in range(output.shape[-1]): viz.show_image(output[0,:,:,i])


