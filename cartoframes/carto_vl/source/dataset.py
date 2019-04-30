from __future__ import absolute_import
from .source import Source
from .source_types import SourceTypes


class Dataset(Source):
    """Source that gets all the data from a Dataset

        Args:
            dataset (str): name of the dataset

        Example:

            .. code::
                from cartoframes import carto_vl as vl
                from cartoframes import CartoContext

                context = CartoContext(
                    base_url='https://cartovl.carto.com/',
                    api_key='default_public'
                )

                vl.Map([
                    vl.Layer(
                        vl.source.Dataset('populated_places')
                    )],
                    context=context
                )
    """

    source_type = SourceTypes.Query

    def __init__(self, dataset):
        query = 'SELECT * FROM {}'.format(dataset)
        super(Dataset, self).__init__(query)
