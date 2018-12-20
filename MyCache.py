import pickle
import os

folder_name = "cached"

def _create_path(filename):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    return '{}/{}.pkl'.format(folder_name, filename)

def create_pickle(filename, data):
    path = _create_path(filename)
    try:
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print("Cached \"{}\"".format(filename))
    except:
        print("Error while create pickle")
        raise

def load_pickle(filename):
    try:
        path = _create_path(filename)
        with open(path, 'rb') as f:
            data = pickle.load(f)
        return data
    except:
        print("Data \"{}\" not found cached".format(filename))
        raise