"""Analysis module"""


class Table(object):
    """Table class for abstract representations of tables in user's CARTO
    account. The list of features is limited in the class now, but will be
    expanded in the future.

    Attributes:

        name (str): Name of table on CARTO account
    """

    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dataset(cls, dataset):
        """Create a Table instance from a dataset name

       Args:
           dataset (str): Name of table on CARTO account
        """
        return cls(str(dataset.name))

    def __repr__(self):
        return 'Table(name={})'.format(self.name)
