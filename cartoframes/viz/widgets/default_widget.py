from ..widget import Widget


def default_widget(title='', description='', footer='', **kwargs):
    """ TODO

    """
    return Widget('default', None, title=title, description=description, footer=footer, **kwargs)
