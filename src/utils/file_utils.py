import constants as C
import imageio
import os.path

def load_image(path):
    return imageio.imread(path)

def save_image(path,img):
    imageio.imsave(path,img)

def export_image(file_name,img):
    imageio.imsave(os.path.join(C.PATH_FOLDER_EXPORTS,file_name),img)

def load_tulip():
    return load_image(C.PATH_FILE_TULIP)