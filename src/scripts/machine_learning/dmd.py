import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *
import matplotlib.pyplot as plt
import cv2

#### TESTS ####


WIDTH = 500
HEIGHT = 1000
K = 950

BLUR_SIZE = 55
OFFSET = 400
image_1 = load_keukenhof()[:HEIGHT, :WIDTH, 0]
image_1 = cv2.GaussianBlur(image_1,(BLUR_SIZE,BLUR_SIZE),0)
image_2 = load_tulip()[OFFSET:OFFSET+HEIGHT, OFFSET:OFFSET+WIDTH, 0]
image_2 = cv2.GaussianBlur(image_2,(BLUR_SIZE,BLUR_SIZE),0)


image_1_x = image_1[:,1]
image_2_x = image_2[:,1]



dmd_input = np.hstack((image_1,image_2))
print('DMD input shape',dmd_input.shape)
dmd_stuff = calculate_dmd(
    dmd_input,return_amplitudes=True,k=K,return_c = False,
    list_motions = [WIDTH,WIDTH])
l,w,a = dmd_stuff

l_inverse = 1 / l
a_1 = (l_inverse[:, None] * np.linalg.pinv(w)) @ image_1_x
a_2 = (l_inverse[:, None] * np.linalg.pinv(w)) @ image_2_x

print(w.shape)
print(l.shape)
print(a.shape)


rec_image_1 = reconstruct_from_dmd(l, w, a_1, num_samples=WIDTH).real
rec_image_1[rec_image_1 < 0] = 0
rec_image_1[rec_image_1 > 255] = 255

rec_image_2 = reconstruct_from_dmd(l, w, a_2, num_samples=WIDTH).real
rec_image_2[rec_image_2 < 0] = 0
rec_image_2[rec_image_2 > 255] = 255

# image_blended = np.hstack((image_1,rec_image_1,image_2,rec_image_2))
# export_image('dmd_test.jpg',image_blended)


NUM_STEPS = 250
animation = np.zeros( (NUM_STEPS,HEIGHT,WIDTH) )
steps = np.linspace(0,1,NUM_STEPS,endpoint=True)

for i,step in enumerate(steps):
    print(step)
    a_intermediary = a_1*(1-step) + step*a_2
    rec_image = reconstruct_from_dmd(l, w, a_intermediary, num_samples=WIDTH).real
    rec_image[rec_image < 0] = 0
    rec_image[rec_image > 255] = 255
    animation[i] = rec_image

export_animation('test.mp4',animation)

# plt.plot( np.abs(a))
# plt.show()
print('DONE')



