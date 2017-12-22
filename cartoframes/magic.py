"""carto magics"""
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from cartoframes.context import CartoContext
from cartoframes import utils
# GOALS
# - have it automatically find a CartoContext object
# - make it agnostic to line or cell magics
# - maps!

def null_to_none(string):
    """changes null to None"""
    return None

@magics_class
class CartoMagics(Magics):
    """Magics for bringing CARTO exploratory data analysis to IPython"""
    @line_cell_magic
    def carto(self, line, cell=None):
        "query carto"
        opts, table = self.parse_options(line, 'c:', posix=False, strict=False)
        if cell:
            query = cell
        else:
            query = 'select * from {}'.format(table)
        context = getattr(opts, 'c', None)
        if context is None:
            # try to find a CartoContext instance if not specified
            for key, val in self.shell.user_ns.items():
                if isinstance(val, CartoContext):
                    context = key
                    break
        if context is None:
            raise ValueError('No CartoContext found or specified')
        evalstr = "{0}.query(\'{1}\')".format(context, query.replace('\n', ' '))
        return eval(evalstr, self.shell.user_ns)

    @line_cell_magic
    def cartomap(self, line, cell=None):
        """carto map"""
        opts, table = self.parse_options(line, 'c:s:iv',
                                         posix=False, strict=False)
        context = getattr(opts, 'c', None)
        stylecol = getattr(opts, 's', None)
        interactive = True if 'i' in opts.keys() else False

        if context is None:
            # try to find a CartoContext instance if not specified
            for key, val in self.shell.user_ns.items():
                if isinstance(val, CartoContext):
                    context = key
                    break
        if context is None:
            raise ValueError('No CartoContext found or specified')
        if stylecol is not None:
            color = utils.pgquote(stylecol)
        else:
            color = None
        if cell:
            layer = 'cartoframes.QueryLayer({query}, color={color})'.format(
                query=utils.pgquote(cell.replace('\n', ' ')),
                color=color)
        else:
            layer = 'cartoframes.Layer({table}, color={color})'.format(
                table=utils.pgquote(table),
                color=color)
        evalstr = "{0}.map({1},interactive={2})".format(context,
                                                         layer,
                                                         interactive)
        if 'v' in opts.keys():
            print(evalstr)

        return eval(evalstr, self.shell.user_ns)

ipython_sess = get_ipython()
ipython_sess.register_magics(CartoMagics)
