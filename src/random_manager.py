import numpy as np

ui32 = np.iinfo(np.uint32)

# the default generator is there to be used by the script itself
# so that is doesn't have to keep it's own special generator
KEY_DEFAULT_GENERATOR = 0
KEY_DEFAULT_BIND_GENERATOR = 1
default_generator = None

CHOICE_KEY = 0
BIND_KEY = 1

# this function must be called first, to properly setup the default random number generator
# if you call the function again, all the previous generators are discarded
def init_def_generator(seed):
    global default_generator
    global default_bind_generator

    default_generator = __generate_random_key__(seed)

def __generate_random_key__(seed):
    intermediate = np.random.RandomState(seed)

    return (
        np.random.RandomState(__random_seed__(intermediate)),
        np.random.RandomState(__random_seed__(intermediate))
    )


def choice(*args,**kwargs):
    return choice_from(default_generator,*args,**kwargs)

def choice_from(key,*args,**kwargs):
    # this is done to make one sampling operation independent from others
    # and thus allow for more sophisticated effects like animation
    seed = __random_seed__(key[CHOICE_KEY])
    return np.random.RandomState(seed).choice(*args,**kwargs)


def __random_seed__(generator):
    return generator.randint(0,ui32.max//2)

def bind_generator():
    return bind_generator_from(default_generator)

def bind_generator_from(key):
    seed = __random_seed__(key[BIND_KEY])
    return __generate_random_key__(seed)

def call_and_bind(function,*args,**kwargs):
    return call_and_bind_from(default_generator,function,*args,**kwargs)

def call_and_bind_from(key,function,*args,**kwargs):
    rkey = bind_generator_from(key)
    return function(*args,**kwargs,rkey=rkey)