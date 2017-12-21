"""carto magics"""
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from cartoframes.context import CartoContext
from cartoframes import utils
# GOALS
# - have it automatically find a CartoContext object
# - make it agnostic to line or cell magics
# - maps!

@magics_class
class CartoMagics(Magics):
    """Magics for bringing CARTO exploratory data analysis to IPython"""
    @line_cell_magic
    def carto(self, line, cell=None):
        "query carto"
        opts, query = self.parse_options(line, 'c:', posix=False, strict=False)
        if cell:
            query = cell
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
        "carto map"
        opts, table = self.parse_options(line, 'c:s:',
                                         posix=False, strict=False)
        context = getattr(opts, 'c', None)
        stylecol = getattr(opts, 's', None)
        if context is None:
            # try to find a CartoContext instance if not specified
            for key, val in self.shell.user_ns.items():
                if isinstance(val, CartoContext):
                    context = key
                    break
        if context is None:
            raise ValueError('No CartoContext found or specified')
        if cell:
            layer = 'QueryLayer({query}, color={color})'.format(
                query=utils.pgquote(cell.replace('\n', ' ')),
                color=utils.pgquote(stylecol))
        else:
            layer = 'Layer({table}, color={color})'.format(
                table=utils.pgquote(table),
                color=utils.pgquote(stylecol))
        evalstr = "{0}.map({1})".format(context, layer)
        return eval(evalstr, self.shell.user_ns)

ipython_sess = get_ipython()
ipython_sess.register_magics(CartoMagics)
