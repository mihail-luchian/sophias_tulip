import numpy as np

def is_listy(thing):
    return hasattr(thing, "__len__")


def listify_if_not_none(thing):
    if thing is None:
        return None
    else:
        return listify(thing)

def array_listify_if_not_none(thing,dtype='int32'):
    l = listify_if_not_none(thing)
    if l is None:
        return None
    else:
        return np.array(l).astype(dtype)

def listify(thing):
    return thing if is_listy(thing) else [thing]

def array_listify(thing,dtype='int32'):
    return np.array(listify(thing)).astype(dtype)
