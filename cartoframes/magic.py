"""IPython Line and Cell Magics"""
from IPython.core.getipython import get_ipython
from IPython.core.magic import (Magics, magics_class, line_cell_magic, register_line_cell_magic)
from cartoframes.context import CartoContext
from cartoframes import utils
# GOALS
# - have it automatically find a CartoContext object
# - make it agnostic to line or cell magics
# - maps!

@magics_class
class CartoMagics(Magics):
    """Line and Cell Magics for bringing CARTO exploratory data analysis to IPython"""

    def find_carto_context(self, context):
        if context is None:
            # try to find a CartoContext instance if not specified
            for key, val in self.shell.user_ns.items():
                if isinstance(val, CartoContext):
                    context = key
                    break
        if context is None:
            raise ValueError('No CartoContext found or specified')
        return context

    @line_cell_magic
    def cartoquery(self, line, cell=None):
        """
        Return results of a query to a CARTO table as a Pandas Dataframe.
        This function can be used both as a line and cell magic.
            - In line mode, you must specify a CARTO table name as a positional
              argument in line. The returned results will be from the query
              `select * from tablename`.
            - In cell mode, you must specify the query in the cell body

        Positional arguments:
            - tablename        a CARTO table name

        Optional arguments:
            - c                An optional argument for specifying a CartoContext
        Returns:
            pandas.DataFrame: DataFrame representation of query on `tablename`
            from CARTO.

        Examples:
            Line magic:
            .. code:: python
                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                %cartoquery -c cc TABLENAME
            Cell magic:
            .. code:: python
                import cartoframes
                creds = cartoframes.Credentials(username='eschbacher', key='abcdefg')
                eschbacher_cc = cartoframes.CartoContext(creds=creds)
                %%cartoquery -cc eschbacher_cc
                SELECT cartodb_id, the_geom from TABLENAME
                LIMIT 2
        """

        opts, table = self.parse_options(line, 'c:', posix=False, strict=False)
        if cell:
            query = cell
        else:
            query = 'select * from {}'.format(table)

        context = opts.get('c', None)
        # try to find a CartoContext instance if not specified
        context = self.find_carto_context(context)

        evalstr = "{0}.query(\'{1}\')".format(context, query.replace('\n', ' '))
        return eval(evalstr, self.shell.user_ns)

    # @magic_arguments()
    # @argument('-c', '--cartocontext', help='An optional argument for '
    #     'specifying a CartoContext')
    # @argument('-s', '--stylecol', help='An optional argument for '
    #     'specifying a column in the table to apply autostyle')
    # @argument('-t', '--timecol', help='An optional argument for '
    #     'specifying a time column in the table to apply a time-animated style')
    # @argument('-i', '--interactive', help='An option for '
    #     'returning a non-interactive static map')
    # @argument('tablename', type=str, help='A string positional argument for table name')
    @line_cell_magic
    def cartomap(self, line, cell=None):
        """
        Return results of a query as a CARTO map.

        This function can be used both as a line and cell magic.
            - In line mode, you must specify a CARTO table name as a positional
              argument in line. The returned mapped results will be from the query
              `select * from tablename`.
            - In cell mode, you must specify the query in the cell body. The query
              must return the column `the_geom_webmercator`

        Positional arguments:
            - tablename        a CARTO table name

        Optional arguments:
            - c                An optional argument for specifying a CartoContext.
                               If no CartoContext is specified, will attempt to search
                               for a CartoContext instance in the IPython session.
            - i                Specify an interactive map; otherwise returns a static map
            - s                Specifying a column by which to apply an autostyle
            - t                Specify a time column to apply a time animated styling
            - v                Print verbose code that generated map

        Returns:
            IPython.display.HTML or matplotlib Axes: Interactive maps are
            rendered as HTML in an `iframe`, while static maps are returned as
            matplotlib Axes objects or IPython Image.

        Examples:
            Line magic:
            .. code:: python
                import cartoframes
                cc = cartoframes.CartoContext(BASEURL, APIKEY)
                %cartomap -c cc my_table

            Cell magic:
            .. code:: python
                import cartoframes
                cc = cartoframes.CartoContext()
                %%cartoquery
                SELECT * from my_table
                WHERE field_1 > 3
        """

        opts, table = self.parse_options(line, 'c:s:ivt:',
                                         posix=False, strict=False)
        context = opts.get('c', None)
        stylecol = opts.get('s', None)
        timecol = opts.get('t', None)
        interactive = True if 'i' in opts else False

        # try to find a CartoContext instance if not specified
        context = self.find_carto_context(context)

        if stylecol is not None:
            stylecol = utils.pgquote(stylecol)

        if timecol is not None:
            timecol = utils.pgquote(timecol)

        if cell:
            layer = 'cartoframes.QueryLayer({query}, color={color}, time={time})'.format(
                query=utils.pgquote(cell.replace('\n', ' ')),
                color=stylecol,
                time=timecol)
        else:
            layer = 'cartoframes.Layer({table}, color={color}, time={time})'.format(
                table=utils.pgquote(table),
                color=stylecol,
                time=timecol)
        evalstr = "{0}.map({1},interactive={2})".format(context,
                                                         layer,
                                                         interactive)
        if 'v' in opts:
            print(evalstr)

        return eval(evalstr, self.shell.user_ns)
#
# if __name__ == '__main__':
#     get_ipython().register_magics(CartoMagics)
try:
    ipython_sess = get_ipython()
    ipython_sess.register_magics(CartoMagics)
except:
    pass
