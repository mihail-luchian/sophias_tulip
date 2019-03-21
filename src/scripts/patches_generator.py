import numpy as np
import utils.generate_utils as gen
import utils.viz_utils as viz
import matplotlib.pyplot as plt

size = (11,11)
imgs = [ gen.random_cross_line(size,seed=i,horizontal=False) for i in range(30) ]
img = np.zeros(size)
for i in imgs: img += i
img[img>=2] = 3

mask = gen.circle(size)

viz.show_image(img*mask)



