"""IPython Line and Cell Magics"""
from IPython.core.getipython import get_ipython
from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.core.magic_arguments import magic_arguments, argument
from cartoframes.context import CartoContext
from cartoframes import utils


@magics_class
class CartoMagics(Magics):
    """Line and Cell Magics for bringing CARTO exploratory data analysis to
    IPython"""

    def find_carto_context(self, context):
        """find the cartocontext if it exists"""
        if context is None:
            # try to find a CartoContext instance if not specified
            for key, val in self.shell.user_ns.items():
                if isinstance(val, CartoContext):
                    context = key
                    break
        if context is None:
            raise ValueError('No CartoContext found or specified')
        return context

    @magic_arguments()
    @argument('-c', '--cartocontext', nargs=1,
              help=('An optional argument for specifying a CartoContext. If '
                    'not specified, an attempt will be made to find one.'))
    @argument('datasource', type=str,
              help=('Tablename if line magic, query if cell magic'))
    @argument('-v', '--verbose', action='store_true',
              help=('If set, this will have the magic print the underlying '
                    'cartoframes code used to produce the output'))
    @line_cell_magic
    def cartoquery(self, line, cell=None):
        """
        Return results of a query to a CARTO table as a pandas DataFrame.
        This magic can be used both as a line and cell magic.

        - In line mode, you must specify a CARTO table name as a positional
          argument in line. The returned results will be from the query
          `SELECT * FROM tablename`. See examples below.
        - In cell mode, you must specify the query in the cell body

        Returns:
            pandas.DataFrame: DataFrame representation of supplied
            `datasource`.

        Examples:

            Line magic:

            .. code:: ipython

                In [1]: import cartoframes
                In [2]: cc = cartoframes.CartoContext(BASEURL, APIKEY)
                In [3]: %cartoquery TABLENAME

            Cell magic:

            .. code:: ipython

                In [1]: import cartoframes
                In [2]: creds = cartoframes.Credentials(
                   ...:     username='acadia',
                   ...:     key='abcdefg')
                In [3]: acadia_cc = cartoframes.CartoContext(creds=creds)
                In [4]: %%cartoquery -c acadia_cc
                   ...: SELECT cartodb_id, the_geom, simpson_index
                   ...: FROM acadia_biodiversity
                   ...: LIMIT 10
        """

        opts, table = self.parse_options(line, 'c:', posix=False, strict=False)
        if cell:
            query = cell
        else:
            query = 'SELECT * FROM {}'.format(table)

        context = opts.get('c', None)
        verbose = True if 'v' in opts else False

        # try to find a CartoContext instance if not specified
        if context is None:
            context = self.find_carto_context(context)

        evalstr = "{0}.query(\'{1}\')".format(
            context, query.replace('\n', ' '))
        if verbose:
            print(evalstr)

        return eval(evalstr, self.shell.user_ns)  # pylint: disable=W0123

    @magic_arguments()
    @argument('-c', '--cartocontext', nargs=1,
              help='An optional argument for specifying a CartoContext')
    @argument('-s', '--stylecol', nargs=1,
              help=('An optional argument for specifying a column in the '
                    'table to apply color autostyle'))
    @argument('-t', '--timecol', nargs=1,
              help=('An optional argument for specifying a time column in the '
                    'table to apply a time-animated style'))
    @argument('-i', '--interactive', action='store_true',
              help='An option for returning a non-interactive static map')
    @argument('-v', '--verbose', action='store_true',
              help=('If set, this will have the magic print the underlying '
                    'cartoframes code used to produce the output'))
    @argument('datasource', type=str,
              help=('tablename if line magic, query if cell magic'))
    @line_cell_magic
    def cartomap(self, line, cell=None):
        """
        Return results of a query as a CARTO map.

        This function can be used both as a line and cell magic.

        - In line mode, you must specify a CARTO table name as a positional
          argument in line. The returned mapped results will be from the query
          `SELECT * FROM tablename`.
        - In cell mode, you must specify the query in the cell body. The query
          must return the column `the_geom_webmercator`

        Returns:
            IPython.display.HTML or matplotlib Axes: Interactive maps are
            rendered as HTML in an `iframe`, while static maps are returned as
            matplotlib Axes objects or IPython Image.

        Examples:
            Line magic:

            .. code:: ipython

                In [1]: import cartoframes
                In [2]: cc = cartoframes.CartoContext(BASEURL, APIKEY)
                In [3]: %cartomap my_table

            Cell magic:

            .. code:: ipython

                In [1]: import cartoframes
                In [2]: cc = cartoframes.CartoContext()
                In [3]: %%cartomap -c simpson_index
                   ...: SELECT simpson_index, species
                   ...: FROM acadia_biodiversity
                   ...: LIMIT 2
                Out[3]:
                    simpson_index species
                0             0.7     per
                1             0.8     fox
        """

        opts, table = self.parse_options(line, 'c:s:ivt:',
                                         posix=False, strict=False)
        context = opts.get('c', None)
        stylecol = opts.get('s', None)
        timecol = opts.get('t', None)
        interactive = True if 'i' in opts else False
        verbose = True if 'v' in opts else False

        # try to find a CartoContext instance if not specified
        if context is None:
            context = self.find_carto_context(context)

        if stylecol is not None:
            stylecol = utils.pgquote(stylecol)

        if timecol is not None:
            timecol = utils.pgquote(timecol)

        if cell:
            layer = ('cartoframes.QueryLayer('
                     '{query}, color={color}, time={time})').format(
                         query=utils.pgquote(cell.replace('\n', ' ')),
                         color=stylecol,
                         time=timecol)
        else:
            layer = ('cartoframes.Layer('
                     '{table}, color={color}, time={time})').format(
                         table=utils.pgquote(table),
                         color=stylecol,
                         time=timecol)
        evalstr = "{0}.map({1},interactive={2})".format(
            context, layer, interactive)
        if verbose:
            print(evalstr)

        return eval(evalstr, self.shell.user_ns)  # pylint: disable=W0123


try:
    ipython_sess = get_ipython()  # pylint: disable=C0103
    ipython_sess.register_magics(CartoMagics)
except AttributeError:
    pass
