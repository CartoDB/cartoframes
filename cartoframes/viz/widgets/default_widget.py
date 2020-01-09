from ..widget import Widget


def default_widget(title='', description='', footer='', **kwargs):
    """ TODO

    """
    return Widget('default', None, title, description, footer, **kwargs)
