import tensorflow as tf



def create_variable(shape,name='var',dev=0.01,seed=1):
    return tf.Variable(
        tf.random_normal(shape, stddev=dev, seed=seed),
        name=name,dtype=tf.float32)

def create_variable_with_value(value,name='var',dev=0.01,seed=1):
    return tf.Variable(
        value, name=name,dtype=tf.float32)
