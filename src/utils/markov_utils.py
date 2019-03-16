import numpy as np

def simulate_markov_chain(transition_matrix, start_probs, length,seed=1):

    num_elems = len(transition_matrix)
    np.random.seed(seed)
    r = np.arange(num_elems)
    pseudo_simulations = np.zeros((num_elems,length)).astype('int32')

    for i in range(num_elems):
        pseudo_simulations[i] = np.random.choice(r,size=length,p=transition_matrix[i])

    start_elem = np.random.choice(r,p=start_probs)

    simulation = np.zeros(length)
    simulation[0] = start_elem
    current_elem = start_elem

    for i in range(1,length):
        new_elem = pseudo_simulations[current_elem,i]
        simulation[i] = new_elem
        current_elem = new_elem

    return simulation.astype('int32')

def simulate_markov_hierarchy(node,length=None,seed=1):

    breakout = False
    iteration = 0
    sim_length = 10 if length is None else length
    while breakout == False:
        current_seed = seed+iteration
        simulation = simulate_markov_chain(
            transition_matrix=node.transition_matrix,
            start_probs=node.start_probs,
            length=sim_length,
            seed=current_seed)
        vals = [node.values[i] for i in simulation]

        if node.leaf is False:
            np.random.seed(current_seed+1)
            child_lens = np.random.choice(node.child_lengths,sim_length)
            for j,(n,l) in enumerate(zip(vals,child_lens)):
                m = simulate_markov_hierarchy(n,l,seed=(current_seed+j)*100)
                for i in m:
                    yield i
        else:
            yield np.array(vals)

        iteration += 1
        if length is not None: breakout = True


def gen_img_markov_hierarchy(markov_tree,height,width,seed=1):
    full_simulation = simulate_markov_hierarchy(markov_tree,seed=seed)

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

    return img.reshape((height,width))


class MarkovModel:

    def __init__(self,
                 preference_matrix=None,
                 start_probs=None,
                 values=None,
                 child_lengths=None):

        l = len(values)
        self.start_probs = np.ones(l)/l if start_probs is None else start_probs
        self.child_lengths = child_lengths
        self.values = values
        self.leaf = True if self.child_lengths is None else False
        self.__init_transition_matrix__(preference_matrix)

    def __init_transition_matrix__(self,preference_matrix):
        self.preference_matrix = preference_matrix
        sums = np.sum(preference_matrix,axis=1)
        self.transition_matrix = self.preference_matrix / sums[:,None]


class SimpleProgression(MarkovModel):

    def __init__(self,
                 values = None,
                 child_lengths = None):

        l = len(values)
        preference_matrix = np.eye(l)
        preference_matrix = np.roll(preference_matrix,1,axis=1)

        super().__init__(
            preference_matrix=preference_matrix,
            start_probs=np.ones(l)/l,
            values=values,
            child_lengths=child_lengths)


class SimplePattern(SimpleProgression):

    def __init__(self,
                 pattern = None,
                 candidates = None,
                 child_lengths = None):

        # example of pattern 001100111101234321

        int_pattern = [int(i) for i in pattern]
        values = [ candidates[i] for i in int_pattern ]

        super().__init__(
            values=values,
            child_lengths=child_lengths)


class FuzzyProgression(MarkovModel):
    def __init__(self,
                 values = None,
                 child_lengths = None,
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
            start_probs=np.ones(l)/l,
            values=values,
            child_lengths=child_lengths)


class RandomMarkovModel(MarkovModel):

    def __init__(self,
                 values=None,
                 child_lengths=None,
                 seed=100):

        l = len(values)
        np.random.seed(seed)
        preference_matrix = np.random.choice(
            np.arange(100),size=(l,l))

        super().__init__(
            preference_matrix=preference_matrix,
            start_probs=np.ones(l)/l,
            values=values,
            child_lengths=child_lengths)