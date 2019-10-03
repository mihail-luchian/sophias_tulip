'''
    The design of the random manager:

    Everything starts with the seed. When init_def_generator (which has to be always called first) is called,
    a default generator is constructed. This default generator can then be used the generate new generators using the
    bind_generator function. It is advisable that you do not use the default generator for anything else.

    Each generator is a tuple which contains the seed with which the generator was created (useful when you want to
    reset the generator) and 2 RandomStates, one for sampling from different distributions and one for creating other
    generators. Additional RandomStates may be added later.

    The reason the generator was designed like this is to
    facilitate as many 'independent' random actions as possible, i.e. when working with randomness you do not want the
    operations in one part of the code, to affect the samples from other parts of the code. This makes development a
    whole lot easier.

'''


import numpy as np

ui32 = np.iinfo(np.uint32)
default_generator = None

__INDEX_START_SEED__ = 0
__INDEX_CHOICE_RANDOM_STATE__ = 1
__INDEX_BIND_RANDOM_STATE__ = 2

# this function must be called first, to properly setup the default random number generator
# if you call the function again, all the previous generators are discarded
def init_def_generator(seed):
    global default_generator
    global default_bind_generator
    default_generator = make_generator(seed)


def make_generator(seed):
    intermediate = np.random.RandomState(seed)

    return (
        seed,
        np.random.RandomState(__random_seed__(intermediate)),
        np.random.RandomState(__random_seed__(intermediate))
    )


def choice(*args,**kwargs):
    return choice_from(default_generator,*args,**kwargs)


def choice_from(generator,*args,**kwargs):
    seed = __random_seed__(generator[__INDEX_CHOICE_RANDOM_STATE__])
    return np.random.RandomState(seed).choice(*args,**kwargs)


def binomial(*args,**kwargs):
    return binomial_from(default_generator,*args,**kwargs)


def binomial_from(generator,*args,**kwargs):
    seed = __random_seed__(generator[__INDEX_CHOICE_RANDOM_STATE__])
    return np.random.RandomState(seed).binomial(*args,**kwargs)


def poisson(*args,**kwargs):
    return poisson_from(default_generator,*args,**kwargs)


def poisson_from(generator,*args,**kwargs):
    seed = __random_seed__(generator[__INDEX_CHOICE_RANDOM_STATE__])
    return np.random.RandomState(seed).poisson(*args,**kwargs)


def uniform(*args,**kwargs):
    return uniform_from(default_generator,*args,**kwargs)


def uniform_from(generator,*args,**kwargs):
    seed = __random_seed__(generator[__INDEX_CHOICE_RANDOM_STATE__])
    return np.random.RandomState(seed).uniform(*args,**kwargs)


def shuffle(*args,**kwargs):
    return shuffle_from(default_generator,*args,**kwargs)


def shuffle_from(generator,*args,**kwargs):
    seed = __random_seed__(generator[__INDEX_CHOICE_RANDOM_STATE__])
    return np.random.RandomState(seed).shuffle(*args,**kwargs)


def get_start_seed(generator):
    return generator[__INDEX_START_SEED__]

def reset_generator(generator):
    return make_generator(get_start_seed(generator))


def random_seed_from(generator):
    return __random_seed__(generator[__INDEX_BIND_RANDOM_STATE__])



def __random_seed__(random_state):
    return random_state.randint(0,ui32.max//2)


def bind_generator():
    return bind_generator_from(default_generator)


def bind_generator_from(generator):
    seed = __random_seed__(generator[__INDEX_BIND_RANDOM_STATE__])
    return make_generator(seed)


def call_and_bind(function,*args,**kwargs):
    return call_and_bind_from(default_generator,function,*args,**kwargs)


def call_and_bind_from(generator,function,*args,**kwargs):
    rgen = bind_generator_from(generator)
    return function(*args,**kwargs,rgen=rgen)