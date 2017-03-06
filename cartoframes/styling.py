

class CartoCSS(object):
    """
        class for constructing CartoCSS
    """
    def __init__(self, df, size=None, color=None):
        """
        """
        self.size = size
        self.color = color
        self.df = df

    def get_size_css(self):
        """
        """
        if self.df.get_carto_geomtype() != 'point':
            raise Exception("Cannot style geometry type `{geomtype}` by "
                            "size.".format(
                geomtype=self.df.get_carto_geomtype()))

        if isinstance(self.size, dict):
            if 'colname' not in self.size:
                raise Exception("Column name not specified.")

            defaults = {'min': 4,
                        'max': 15,
                        'quant_method': 'quantiles'}

            missing_keys = set(defaults) - set(self.size)
            args = dict(self.size, **{k: defaults[k] for k in missing_keys})
            # parse dict
            css = ("marker-width: ramp([{colname}], range({min}, {max}),"
                   "{quant_method}());").format(**args)
            return css
        elif isinstance(self.size, str):
            # parse string
            if self.size in self.df.columns:
                # if string is a column name
                # size by 'reasonable' values
                css = ("marker-width: ramp([{colname}], range(4, 15),"
                       "quantiles());").format(colname=self.size)
                return css
            else:
                raise Exception('`{}` is not a column name.'.format(self.size))
        elif isinstance(self.size, float) or isinstance(self.size, int):
            css = "marker-width: {};".format(self.size)
            return css
        else:
            # return red
            return '#F00'

    def get_color_css(self):
        """
        """
        pass
