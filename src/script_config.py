import constants as C

CONFIG = {
    C.CONFIG_KEY_SUBMISSION : 28
}

def get(key,default):
    if key in CONFIG:
        return CONFIG[key]
    else:
        return default