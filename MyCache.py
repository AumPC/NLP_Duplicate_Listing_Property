import pickle
import os

folder_name = "cached"

def _create_path(filename):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    return '{}/{}.pkl'.format(folder_name, filename)

def create_pickle(filename, data, DEBUG):
    path = _create_path(filename)
    try:
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        if DEBUG:
            print("Cached \"{}\"".format(filename))
    except:
        if DEBUG:
            print("Error while create pickle")
        raise

def load_pickle(filename, DEBUG):
    try:
        path = _create_path(filename)
        with open(path, 'rb') as f:
            data = pickle.load(f)
        return data
    except:
        if DEBUG:
            print("Data \"{}\" not found cached".format(filename))
        raise