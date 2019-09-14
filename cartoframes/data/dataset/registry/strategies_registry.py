from .dataframe_dataset import DataFrameDataset
from .query_dataset import QueryDataset
from .table_dataset import TableDataset


class StrategiesRegistry(object):
    """Class for managing all the strategies possible of a Dataset.
    It is implemented following the Singleton pattern.

    Example:

        Add a new strategy:

        .. code::
        from cartoframes.data import StrategiesRegistry

        strategyRegistry = StrategiesRegistry()
        strategyRegistry.add(CSVDataset)
    """
    class __StrategiesRegistry:
        def __init__(self, strategies):
            self.registry = strategies

    instance = None

    def __init__(self):
        if not StrategiesRegistry.instance:
            StrategiesRegistry.instance = StrategiesRegistry.__StrategiesRegistry(self._get_initial_strategies())

    def _get_initial_strategies(self):
        return [DataFrameDataset, QueryDataset, TableDataset]

    def get_strategies(self):
        return StrategiesRegistry.instance.registry

    def add(self, strategy):
        StrategiesRegistry.instance.registry.append(strategy)
