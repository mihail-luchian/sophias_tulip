import numpy as np
import constants as c


def is_listy(thing):
    return hasattr(thing, "__len__")


def listify(thing):
    return thing if is_listy(thing) else [thing]


def markov_model_is_leaf(values):
    # we examine two cases:
    # the values might be just a list, then we look only at the first element
    # the values is a list of list and then we have to look at the first element of the first list

    if is_listy(values[0]) and hasattr(values[0][0],'type'):
        return False
    elif hasattr(values[0],'type'):
        return False
    else:
        return True


def simulate_markov_chain(node,length):
    if node.update_step is None or node.update_fun is None:
        return simulate_markov_chain_without_update(
            transition_matrix=node.transition_matrix,
            start_probs=node.start_probs,
            length=length)
    else:
        return simulate_markov_chain_with_update(node,length)

def simulate_markov_chain_without_update(transition_matrix, start_probs, length):

    num_elems = len(transition_matrix)
    r = np.arange(num_elems)
    pseudo_simulations = np.zeros((num_elems,length)).astype('int32')

    for i in range(num_elems):
        s = np.random.choice(r,size=length,p=transition_matrix[i])
        pseudo_simulations[i] = s

    start_elem = np.random.choice(r,p=start_probs)

    simulation = np.zeros(length)
    simulation[0] = start_elem
    current_elem = start_elem

    for i in range(1,length):
        new_elem = pseudo_simulations[current_elem,i]
        simulation[i] = new_elem
        current_elem = new_elem

    return simulation.astype('int32')



def simulate_markov_chain_with_update(node, length):

    current_length = 0
    first_step = node.update_step - node.simulated_length % node.update_step
    simulations = []
    while current_length < length:
        sim_length = node.update_step if current_length > 0 else first_step
        current_length += sim_length

        simulations += [ simulate_markov_chain_without_update(
            node.transition_matrix,node.start_probs,sim_length) ]

        update_node(node)

    simulation = np.concatenate(simulations)[:length]
    node.simulated_length += length
    return simulation


def update_node(node):
    new_preference_matrix, new_start_probs = node.update_fun(
        node.preference_matrix, node.start_probs)

    node.preference_matrix = new_preference_matrix
    node.transition_matrix = compute_transition_matrix(node.preference_matrix)
    node.start_probs = new_start_probs / np.sum(new_start_probs)


def simulate_markov_generator(node, length=None):

    breakout = False
    iteration = 0
    # if length is None, this means we are simulating the parent
    # if length is -1, this means no length for the children has been specified
    #   and in this case we use the self_length
    sim_length = 10 if length is None else length
    if sim_length == -1:
        sim_length = np.random.choice(node.self_length)
    while breakout == False:
        simulation = simulate_markov_chain(node=node,length=sim_length)

        if node.lengths is not None:
            repeats = [ node.lengths[s] for s in simulation  ]
            simulation = np.repeat(simulation,repeats)
        vals = [node.values[i] for i in simulation]


        if node.leaf is False:

            child_lens = np.random.choice(node.child_lengths,sim_length)
            for j,(n,l) in enumerate(zip(vals,child_lens)):
                m = simulate_markov_hierarchy(n,l)
                for i in m:
                    yield i
        else:

            yield np.array(vals)

        iteration += 1
        if length is not None:
            breakout = True


def simulate_markov_processor(node,length):
    m = simulate_markov_hierarchy(node.node,length)
    ms = []
    for i in m:
        ms += [i]

    vals = np.concatenate(ms)
    total_size = vals.size
    if node.length_limit is not None and total_size >= node.length_limit:
        vals = vals[:node.length_limit]

    reps = np.random.choice(node.num_tiles)
    vals = np.tile(vals, reps)

    yield vals


def simulate_markov_hierarchy(node,length=None):
    if node.type == c.TYPE_GEN:
        sim = simulate_markov_generator(node, length)
    elif node.type == c.TYPE_PROC:
        sim = simulate_markov_processor(node,length)
    for i in sim:
        yield i


def paint_linearly_markov_hierarchy(
        markov_tree,
        height, width,
        tile_height = None,
        tile_width = None):
    full_simulation = simulate_markov_hierarchy(markov_tree)

    full_img_len = height * width
    current = 0
    img = np.zeros(height * width)
    for i in full_simulation:
        l = i.size
        img_start = current
        img_end = img_start + l
        gen_end = l
        if img_end >= full_img_len:
            img_end = full_img_len
            gen_end = img_end - img_start

        img[img_start:img_end] = i[:gen_end]
        current = img_end
        if current >= full_img_len - 1:
            break

    if tile_height is not None and tile_width is not None:
        img = img.reshape((-1,tile_width))
        new_img = np.zeros((height,width),dtype=img.dtype)
        num_tiles_h = height//tile_height
        num_tiles_w = width//tile_width
        for i in range(num_tiles_h):
            for j in range(num_tiles_w):
                start_h = i*tile_height
                start_w = j*tile_width
                s = np.s_[start_h:start_h+tile_height,start_w:start_w+tile_width]

                idx = (i*num_tiles_w + j)*tile_height
                new_img[s] = img[idx:idx+tile_height,:]

        return new_img
    else:
        return img.reshape((height,width))


def compute_transition_matrix(preference_matrix):
    sums = np.sum(preference_matrix, axis=1)
    return preference_matrix / sums[:, None]

class MarkovModel:

    def __init__(self,
                 preference_matrix=None,
                 start_probs=None,
                 values=None,
                 child_lengths=-1,
                 lenghts=None,
                 self_length=None,
                 update_step=None,
                 update_fun=None):

        l = len(values)
        self.values = listify(values)

        # child_lengths is one way one can deduce if is leaf node or not
        self.child_lengths = np.array(listify(child_lengths)).astype('int32')
        self.lengths = None if lenghts is None else np.array(lenghts).astype('int32')
        self.self_length = None if self_length is None else np.array(listify(self_length)).astype('int32')
        self.type = c.TYPE_GEN

        if start_probs is None:
            self.start_probs = np.ones(l)/l
        elif is_listy(start_probs) and len(start_probs) == l:
            self.start_probs = start_probs / np.sum(start_probs)
        else:
            self.start_probs = np.zeros(l)
            start_probs = listify(start_probs)
            self.start_probs[start_probs] = 1/len(start_probs)

        self.leaf = markov_model_is_leaf(values)
        self.preference_matrix = np.array(preference_matrix)
        self.transition_matrix = compute_transition_matrix(self.preference_matrix)

        self.update_step = update_step
        self.update_fun = update_fun
        self.simulated_length = 0



class SimpleProgression(MarkovModel):

    def __init__(self, values = None,**kwargs):

        values = listify(values)
        l = len(values)
        preference_matrix = np.eye(l)
        preference_matrix = np.roll(preference_matrix,1,axis=1)

        super().__init__(
            preference_matrix=preference_matrix,
            values=values,
            **kwargs)


class SimplePattern(SimpleProgression):

    def __init__(self,
                 pattern = None,
                 candidates = None,
                 **kwargs):

        # example of pattern 001100111101234321


        int_pattern = [int(i) for i in pattern]
        values = [ candidates[i] for i in int_pattern ]
        super().__init__(
            values=values,
            **kwargs)


class FuzzyProgression(MarkovModel):
    def __init__(self,
                 values = None,
                 child_lengths = None,
                 start_probs = None,
                 positive_shifts = 1,
                 negative_shifts = 0,
                 repeat_factor = 1
                 ):

        l = len(values)

        base = np.eye(l)
        preference_matrix = base*repeat_factor
        for i in range(positive_shifts):
            preference_matrix += np.roll(base,i+1,axis=1)
        for i in range(negative_shifts):
            preference_matrix += np.roll(base,-(i+1),axis=1)

        super().__init__(
            preference_matrix=preference_matrix,
            start_probs=start_probs,
            values=values,
            child_lengths=child_lengths)


class RandomMarkovModel(MarkovModel):

    def __init__(self, values=None, **kwargs):


        values = listify(values)
        l = len(values)
        preference_matrix = np.random.choice(
            np.arange(100),size=(l,l))

        super().__init__(
            preference_matrix=preference_matrix,
            values=values,
            **kwargs)


class Processor:
    def __init__(self, node, num_tiles=1, length_limit=None):
        self.node = node
        self.num_tiles = num_tiles if hasattr(num_tiles, "__len__") else [num_tiles]
        self.length_limit = length_limit
        self.type = c.TYPE_PROC
