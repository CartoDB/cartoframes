from __future__ import absolute_import

from .legend import Legend


class LegendList(object):
    """LegendList
     Args:
        legends (dict, list, Legend): List of legends for a layer.

    Example:

        .. code::python

            from cartoframes.viz import legend

            LegendList([])
    """

    def __init__(self, legends=None):
        self._legends = self._init_legends(legends)

    def _init_legends(self, legends):
        if isinstance(legends, list):
            legend_list = []
            for legend in legends:
                if isinstance(legend, (dict, str)):
                    legend_list.append(Legend(legend))
                elif isinstance(legend, Legend):
                    legend_list.append(legend)
            return legend_list
        if isinstance(legends, dict):
            return [Legend(legends)]
        elif isinstance(legends, Legend):
            return [legends]
        else:
            return []

    def get_info(self, geom_type=None):
        legends_info = []
        for legend in self._legends:
            if legend:
                legends_info.append(legend.get_info(geom_type))

        return legends_info
