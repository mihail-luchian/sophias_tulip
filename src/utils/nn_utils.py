import tensorflow as tf
import random_manager as r
import numpy as np


def create_variable(shape,name='var',dev=0.01,rgen=None):

    seed = None
    if rgen is not None:
        seed = r.random_seed_from(rgen)
    return tf.Variable(
        tf.random_normal(shape, stddev=dev, seed = seed),
        name=name,dtype=tf.float32)

def create_variable_with_value(value,name='var'):
    return tf.Variable(
        value, name=name,dtype=tf.float32)

def dense_layer(input,size,rgen,activation=None,wdev=0.01,bdev=0.01):

    w = create_variable(
        [input.shape.as_list()[1],size],name='w',dev=wdev,
        rgen=r.bind_generator_from(rgen))
    b = create_variable(
        [size],name='b',dev=bdev,
        rgen=r.bind_generator_from(rgen))

    layer = tf.add(tf.matmul(input, w), b)

    if activation is not None:
        layer = activation(layer)

    return layer


def make_batch_generator(input,labels=None,batch_size=32, rgen=None):
    data_len = input.shape[0]
    indices = np.arange(data_len)
    if rgen is not None:
        r.shuffle_from(rgen,indices)

    num_batches = data_len // batch_size

    def batch_generator():
        for i in range(num_batches):
            samples = indices[i*batch_size:(i+1)*batch_size]
            if labels is None:
                yield input[samples]
            else:
                yield input[samples],labels[samples]

    return batch_generator(),num_batches




