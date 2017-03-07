"""
"""

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

    def check_size_inputs(self, inputs):
        """Checks whether the inputs are valid
        """
        import numbers
        if isinstance(inputs, dict):
            if 'colname' not in self.size:
                raise NameError("Column name not specified.")
            elif inputs['colname'] not in self.df.columns:
                raise NameError("Column name `{}` not in "
                                "cartoframe.".format(inputs['colname']))
            elif inputs['min'] >= inputs['max']:
                raise ValueError("Min size must be larger than max size.")
            elif inputs['min'] < 0 or inputs['max'] < 0:
                raise ValueError("Min and max sizes must be greater than or "
                                 "equal to zero.")
        elif isinstance(inputs, str):
            if inputs not in self.df.columns:
                raise NameError("Column name `{}` not in "
                                "cartoframe.".format(inputs['colname']))
        elif isinstance(inputs, numbers.Number):
            if inputs <= 0:
                raise ValueError("Marker width must be greater than zero. "
                                 "`{}` was input.".format(inputs))

        if self.df.get_carto_geomtype() != 'point':
            raise Exception("Cannot style geometry type `{geomtype}` by "
                            "size.".format(
                geomtype=self.df.get_carto_geomtype()))

        return None

    def get_size_css(self):
        """
        """
        import numbers

        if isinstance(self.size, dict):
            # TODO: check with mamata on cartographic best-practices
            defaults = {'min': 4,
                        'max': 15,
                        'quant_method': 'quantiles'}

            missing_keys = set(defaults) - set(self.size)
            args = dict(self.size, **{k: defaults[k] for k in missing_keys})
            self.check_size_inputs(args)
            # parse dict
            css = ("marker-width: ramp([{colname}], range({min}, {max}), "
                   "{quant_method}());").format(**args)
            return css
        elif isinstance(self.size, str):
            self.check_size_inputs(self.size)
            # parse string
            if self.size in self.df.columns:
                # if string is a column name
                # size by 'reasonable' values
                css = ("marker-width: ramp([{colname}], range(4, 15), "
                       "quantiles());").format(colname=self.size)
                return css
            else:
                raise Exception('`{}` is not a column name.'.format(self.size))
        elif isinstance(self.size, numbers.Number):
            self.check_size_inputs(self.size)
            css = "marker-width: {};".format(self.size)
            return css
        else:
            # return red
            return "marker-width: 7;"

    def get_color_css(self):
        """
        """
        import numbers
        if isinstance(self.size, dict):
            # TODO: check with mamata on cartographic best-practices

            # choose category or quantitative defaults
            if self.df[self.size['colname']].dtype == :
                defaults = {'ramp': 'RedOr',
                            'quant_method': 'quantiles'}
            else:
                defaults = {'ramp': 'Bold',
                            'quant_method': 'category'}

            missing_keys = set(defaults) - set(self.size)
            args = dict(self.size, **{k: defaults[k] for k in missing_keys})
            self.check_size_inputs(args)
            # parse dict
            css = ("marker-width: ramp([{colname}], range({min}, {max}), "
                   "{quant_method}());").format(**args)
            return css
        elif isinstance(self.size, str):
            self.check_size_inputs(self.size)
            # parse string
            if self.size in self.df.columns:
                # if string is a column name
                # size by 'reasonable' values
                css = ("marker-width: ramp([{colname}], range(4, 15), "
                       "quantiles());").format(colname=self.size)
                return css
            else:
                raise Exception('`{}` is not a column name.'.format(self.size))
        elif isinstance(self.size, numbers.Number):
            self.check_size_inputs(self.size)
            css = "marker-width: {};".format(self.size)
            return css
        else:
            # return red
            return "marker-width: 7;"
