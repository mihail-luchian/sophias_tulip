### SUBMISSION_25

CONFIG = {
}

def get(key,default):
    if key in CONFIG:
        return CONFIG[key]
    else:
        return default