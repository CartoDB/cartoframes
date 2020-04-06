from .legend import Legend
from .constants import SINGLE_LEGEND


class LegendList:
    """LegendList
        Args:
            legends (list, Legend): List of legends for a layer.

    """

    def __init__(self, legends=None, default_legend=None, geom_type=None):
        self._legends = self._init_legends(legends, default_legend, geom_type)

    def _init_legends(self, legends, default_legend, layer_type):
        if isinstance(legends, list):
            legend_list = []
            for legend in legends:
                if isinstance(legend, Legend):
                    if legend._type == 'default' or legend._type == 'basic':
                        legend._type = _get_simple_legend_geometry_type(layer_type)
                    if legend._type == 'default' and default_legend:
                        legend._prop = default_legend._prop
                    legend_list.append(legend)
                else:
                    raise ValueError('Legends list contains invalid elements')
            return legend_list
        else:
            return []

    def get_info(self):
        legends_info = []
        for legend in self._legends:
            if legend:
                legends_info.append(legend.get_info())

        return legends_info


def _get_simple_legend_geometry_type(layer_type):
    return SINGLE_LEGEND + '-' + layer_type
