import constants as C
import imageio
import os.path

def load_image(path):
    return imageio.imread(path)

def save_image(path,img):
    imageio.imsave(path,img)

def export_image(file_name,img):
    imageio.imsave(os.path.join(C.PATH_FOLDER_EXPORTS,file_name),img)



# simple functions to load images that come with the scripts
def load_tulip():
    return load_image(C.PATH_FILE_TULIP)

def load_tulip_low():
    return load_image(C.PATH_FILE_TULIP_LOW)

def load_keukenhof():
    return load_image(C.PATH_FILE_KEUKENHOF)

def load_keukenhof_low():
    return load_image(C.PATH_FILE_KEUKENHOF_LOW)