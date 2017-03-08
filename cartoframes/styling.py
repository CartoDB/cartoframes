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

    def check_color_inputs(self, inputs):
        """Checks whether the inputs are valid
        """
        import numbers
        quant_methods = {'quantiles', 'jenks', 'headtails',
                         'equal', 'category'}
        ramp_providers = {'cartocolor', 'colorbrewer'}

        if isinstance(inputs, dict):
            if 'colname' not in self.color:
                raise NameError("Column name not specified.")
            elif inputs['colname'] not in self.df.columns:
                raise NameError("Column name `{}` not in "
                                "cartoframe.".format(inputs['colname']))
            elif inputs['quant_method'] not in quant_methods:
                raise ValueError(
                    ("`quant_method` must be one of "
                     "{methods}. `{provided}` was "
                     "entered").format(methods=', '.join(quant_methods),
                                       provided=inputs['quant_method']))
            elif inputs['ramp_provider'] not in ramp_providers:
                raise ValueError(
                    ("`ramp_provider` must be one of "
                     "{methods}. `{provided}` was "
                     "entered").format(methods=', '.join(ramp_providers),
                                       provided=inputs['ramp_provider']))
            elif (not isinstance(inputs['ramp'], str) and
                      not isinstance(inputs['ramp'], list) and
                      not isinstance(inputs['ramp'], tuple)):
                raise TypeError("`ramp` param must be of type string")
            elif not isinstance(inputs['quant_method'], str):
                raise TypeError("`quant_method` must be of type string.")
            elif not isinstance(inputs['ramp_provider'], str):
                raise TypeError("`ramp_provider` must be of type string.")
        elif isinstance(inputs, str):
            if inputs not in self.df.columns and inputs[0] != '#':
                raise NameError("`{}` is not a valid column name or "
                                "hex color. Hex values should begin with a " "`#`.".format(inputs['colname']))
        else:
            raise TypeError("Expecting a dict or a string.")

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
            self.check_color_inputs(args)
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
            if self.df[self.size['colname']].dtype in ('float64', 'int64'):
                defaults = {'ramp': 'RedOr',
                            'ramp_provider': 'cartocolor',
                            'quant_method': 'quantiles',
                            'num_bins': ''}
            else:
                defaults = {'ramp': 'Bold',
                            'ramp_provider': 'cartocolor',
                            'quant_method': 'category',
                            'num_bins': ''}

            missing_keys = set(defaults) - set(self.size)
            args = dict(self.size, **{k: defaults[k] for k in missing_keys})
            self.check_color_inputs(args)

            # convert items to comma-separated list if appropriate
            if not isinstance(args['ramp'], str):
                args['num_bins'] = len(args['ramp'])
                args['ramp'] = ', '.join([str(r) for r in args['ramp']])

            # parse dict
            css = ("marker-fill: ramp([{colname}], {ramp_provider}({ramp}), "
                   "{quant_method}({num_bins}));").format(**args)
            return css
        elif isinstance(self.color, str) and self.color in self.df.columns:
            self.check_size_inputs(self.color)
            default_quant = ('quantiles' if self.df[self.color].dtype in
                                 ('float64', 'int64')
                             else 'category')
            defaults = {'ramp_provider': 'cartocolor',
                        'ramp': 'RedOr',
                        'quant_method': default_quant}
            args = dict(defaults, **{'colname': self.color})
            # parse string
            if self.size in self.df.columns:
                # if string is a column name
                css = ("marker-fill: ramp([{colname}], "
                       "{ramp_provider}({ramp}), "
                       "{quant_method}({num_bins}));").format(**args)
                return css
            else:
                css = "marker-fill: {};".format(self.size)
                return css
        else:
            # return red
            return "marker-fill: #f00;"
