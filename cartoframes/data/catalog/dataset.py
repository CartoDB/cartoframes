
class Dataset(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Datasets(list):
    def __init__(self, items):
        super(Datasets, self).__init__(items)