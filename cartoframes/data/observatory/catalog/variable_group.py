from .entity import CatalogEntity
from .repository.variable_group_repo import get_variable_group_repo
from .repository.variable_repo import get_variable_repo
from .repository.constants import VARIABLE_GROUP_FILTER


class VariableGroup(CatalogEntity):

    _entity_repo = get_variable_group_repo()

    @property
    def variables(self):
        """Get the list of variables included in this variable group.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Variable instances.

        """
        return get_variable_repo().get_all({VARIABLE_GROUP_FILTER: self.id})

    @property
    def name(self):
        """Name of this variable group."""
        return self.data['name']

    @property
    def dataset(self):
        """ID of the dataset related to this variable group."""
        return self.data['dataset_id']
