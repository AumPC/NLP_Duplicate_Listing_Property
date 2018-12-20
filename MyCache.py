import pickle

folder_name = "cached"

def _create_path(filename):
    return '{}/{}.pkl'.format(folder_name, filename)

def create_pickle(filename, data):
    path = _create_path(filename)
    try:
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    except:
        print("Error while create pickle")
    finally:
        f.close()

def load_pickle(filename):
    try:
        path = _create_path(filename)
        with open(path, 'rb') as f:
            data = pickle.load(f)
        return data
    except:
        print("Data not found")
        return None
    finally:
        f.close()