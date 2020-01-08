from .legend import Legend


class LegendList:
    """LegendList
        Args:
            legends (list, Legend): List of legends for a layer.

    """
    def __init__(self, legends=None, default_legend=None):
        self._legends = self._init_legends(legends, default_legend)

    def _init_legends(self, legends, default_legend):
        if isinstance(legends, list):
            legend_list = []
            for legend in legends:
                if isinstance(legend, Legend):
                    # FIXME
                    if legend._type == 'default' and default_legend:
                        legend._type = default_legend._type
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
