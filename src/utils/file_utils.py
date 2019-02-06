import constants as C
import imageio
import os.path

def load_image(path):
    return imageio.imread(path)

def save_image(path,img):
    imageio.imsave(path,img)

def export_image(file_name,img):
    imageio.imsave(os.path.join(C.PATH_FOLDER_EXPORTS,file_name),img)

def export_animation(file_name,animation,loop = 1):
    writer = imageio.get_writer(os.path.join(C.PATH_FOLDER_EXPORTS,file_name), fps=25)
    for cycle in range(loop):
        for i in range(animation.shape[0]):
            writer.append_data(animation[i])
    writer.close()



# simple functions to load images that come with the scripts
def load_tulip():
    return load_image(C.PATH_FILE_TULIP)

def load_tulip_low():
    return load_image(C.PATH_FILE_TULIP_LOW)

def load_keukenhof():
    return load_image(C.PATH_FILE_KEUKENHOF)

def load_keukenhof_low():
    return load_image(C.PATH_FILE_KEUKENHOF_LOW)