import tensorflow as tf
from tensorflow import keras
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


### Custom layers

class SinLayer(keras.layers.Layer):

    def __init__(self,seed_bias,seed_scale, **kwargs):
        self.seed_bias = seed_bias
        self.seed_scale = seed_scale
        super(SinLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        bias_initializer = keras.initializers.RandomUniform(
            minval=-np.pi, maxval=np.pi, seed=self.seed_bias)
        scale_initializer = keras.initializers.RandomUniform(
            minval=0.2, maxval=2, seed=self.seed_scale)

        # Create a trainable weight variable for this layer.
        self.bias = self.add_weight(
            name='bias',
            shape=(input_shape[1],),
            initializer=bias_initializer,
            trainable=True)
        self.scale = self.add_weight(
            name='scale',
            shape=(input_shape[1],),
            initializer=scale_initializer,
            trainable=True)
        super(SinLayer, self).build(input_shape)

    def call(self, x):
        return keras.backend.cos( self.scale * np.pi * x - self.bias)

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):

        my_config = {
            'seed_scale' : self.seed_scale,
            'seed_bias'  : self.seed_bias
        }
        base_config = super(SinLayer, self).get_config()
        my_config.update(base_config)
        return my_config


class XYCombinations(keras.layers.Layer):

    def __init__(self,seed_bias,seed_scale, **kwargs):
        self.seed_bias = seed_bias
        self.seed_scale = seed_scale
        super(XYCombinations, self).__init__(**kwargs)

    def build(self, input_shape):
        bias_initializer = keras.initializers.RandomUniform(
            minval=-1, maxval=1, seed=self.seed_bias)
        scale_initializer = keras.initializers.RandomUniform(
            minval=-1, maxval=1, seed=self.seed_scale)

        # Create a trainable weight variable for this layer.
        self.bias = self.add_weight(
            name='bias',
            shape=(4,),
            initializer=bias_initializer,
            trainable=True)
        self.scale = self.add_weight(
            name='scale',
            shape=(4,),
            initializer=scale_initializer,
            trainable=True)
        super(XYCombinations, self).build(input_shape)

    def call(self, x):
        xx = tf.gather(x,[0],axis=1)
        yy = tf.gather(x,[1],axis=1)
        combinations = tf.concat([
            xx*yy,
            xx**2,
            yy**2,
            yy**2 * xx**2,
        ], axis = 1)
        return self.scale*combinations - self.bias

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):

        my_config = {
            'seed_scale' : self.seed_scale,
            'seed_bias'  : self.seed_bias
        }
        base_config = super(XYCombinations, self).get_config()
        my_config.update(base_config)
        return my_config



class CombinatoryMultiplication(keras.layers.Layer):

    def __init__(self,n, **kwargs):

        self.n = n
        yy,xx = np.meshgrid(np.arange(n),np.arange(n))
        tril_indices = np.tril_indices(n=n,k=-1)
        self.yy_indices = yy[tril_indices].flatten()
        self.xx_indices = xx[tril_indices].flatten()

        super(CombinatoryMultiplication, self).__init__(**kwargs)

    def build(self, input_shape):
        super(CombinatoryMultiplication, self).build(input_shape)

    def call(self, x):
        return tf.multiply(
            tf.gather(x,self.xx_indices,axis=1),
            tf.gather(x,self.yy_indices,axis=1),
        )

    def compute_output_shape(self, input_shape):
        return (input_shape[0],self.xx_indices.shape[0])

    def get_config(self):

        my_config = {
            'n' : self.n,
            # 'xx_indices' : self.xx_indices,
            # 'yy_indices' : self.yy_indices
        }
        base_config = super(CombinatoryMultiplication, self).get_config()
        my_config.update(base_config)
        return my_config



