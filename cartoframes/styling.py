"""
"""

class CartoCSS(object):
    """
        class for constructing CartoCSS
    """
    def __init__(self, df, size=None, color=None, cartocss=None):
        """
        """
        self.df = df
        self.size = size
        self.color = color
        self.cartocss = cartocss

    def get_cartocss(self):
        """Given options for CartoCSS styling, return
        CartoCSS
        """
        if self.cartocss is None:
            # get cartocss by geometry type
            css_template = self.cartocss_by_geom(self.df.get_carto_geomtype())

            # fill in based on user inputs
            css_filled = css_template % {'fillstyle': self.get_color_css(),
                                         'sizestyle': self.get_size_css()}
            return css_filled
        else:
            return self.cartocss

    def get_markercss(self):
        """Return CartoCSS for points"""
        markercss = ''.join(
            ("#layer { ",
             "marker-width: %(sizestyle)s; ",
             "marker-fill: %(fillstyle)s; ",
             "marker-fill-opacity: 1; ",
             "marker-allow-overlap: true; ",
             "marker-line-width: 1; ",
             "marker-line-color: #FFF; ",
             "marker-line-opacity: 1; ",
             "}"))
        return markercss

    def get_linecss(self):
        """Return CartoCSS template for lines"""
        linecss = ''.join(
            ("#layer { ",
             "line-width: 1.5; ",
             "line-color: %(fillstyle)s; ",
             "}"))
        return linecss

    def get_polygoncss(self):
        """Return CartoCSS template for polygons"""
        polygoncss = ''.join(
            ("#layer { ",
             "polygon-fill: %(fillstyle)s; ",
             "line-width: 0.5; ",
             "line-color: #FFF; ",
             "line-opacity: 0.5; ",
             "}"))
        return polygoncss

    def cartocss_by_geom(self, geomtype):
        """Return CartoCSS template by geometry type"""

        cartocss = {'point': self.get_markercss(),
                    'line': self.get_linecss(),
                    'polygon': self.get_polygoncss()}

        try:
            return cartocss[geomtype]
        except KeyError:
            raise ValueError("No CartoCSS for type `{}`".format(geomtype))

        return None

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
                raise TypeError("`ramp` param must be of type string, list, "
                                "or tuple.")
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
            defaults = {'min': 4,
                        'max': 15,
                        'quant_method': 'quantiles'}

            missing_keys = set(defaults) - set(self.size)
            args = dict(self.size, **{k: defaults[k] for k in missing_keys})
            self.check_size_inputs(args)
            # parse dict
            css = ("ramp([{colname}], range({min}, {max}), "
                   "{quant_method}())").format(**args)
            return css
        elif isinstance(self.size, str):
            self.check_size_inputs(self.size)
            # parse string
            if self.size in self.df.columns:
                # if string is a column name
                # size by 'reasonable' values
                css = ("ramp([{colname}], range(4, 15), "
                       "quantiles())").format(colname=self.size)
                return css
            else:
                raise Exception('`{}` is not a column name.'.format(self.size))
        elif isinstance(self.size, numbers.Number):
            self.check_size_inputs(self.size)
            css = str(self.size)
            return css
        else:
            # return red
            return "7"

    def get_color_css(self):
        """
        """
        if isinstance(self.color, dict):

            # choose category or quantitative defaults
            if self.df[self.color['colname']].dtype in ('float64', 'int64'):
                defaults = {'ramp': 'RedOr',
                            'ramp_provider': 'cartocolor',
                            'quant_method': 'quantiles',
                            'num_bins': ''}
            else:
                defaults = {'ramp': 'Bold',
                            'ramp_provider': 'cartocolor',
                            'quant_method': 'category',
                            'num_bins': ''}

            missing_keys = set(defaults) - set(self.color)
            args = dict(self.color, **{k: defaults[k] for k in missing_keys})
            self.check_color_inputs(args)

            # convert items to comma-separated list if appropriate
            if not isinstance(args['ramp'], str):
                args['num_bins'] = len(args['ramp'])
                args['ramp'] = ', '.join([str(r) for r in args['ramp']])

            # parse dict
            css = ("ramp([{colname}], {ramp_provider}({ramp}), "
                   "{quant_method}({num_bins}))").format(**args)
            return css
        elif isinstance(self.color, str) and self.color in self.df.columns:
            self.check_color_inputs(self.color)
            print(self.color)
            if self.df[self.color].dtype in ('float64', 'int64'):
                default_quant = 'quantiles'
                default_ramp = 'RedOr'
            else:
                default_quant = 'category'
                default_ramp = 'Bold'
            defaults = {'ramp_provider': 'cartocolor',
                        'ramp': default_ramp,
                        'quant_method': default_quant,
                        'num_bins': 7}
            args = dict(defaults, **{'colname': self.color})
            # parse string
            if self.color in self.df.columns:
                # if string is a column name
                css = ("ramp([{colname}], "
                       "{ramp_provider}({ramp}), "
                       "{quant_method}({num_bins}))").format(**args)
                print(css)
                return css
            else:
                return self.color
        else:
            # return red
            return "#f00"
