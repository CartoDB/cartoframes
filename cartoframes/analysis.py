class Table:

    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dataset(cls, dataset):
        return cls(dataset.name)
