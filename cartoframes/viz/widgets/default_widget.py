from ..widget import Widget


def default_widget(title='', description='', footer=''):
    return Widget('default',
                  title=title,
                  description=description,
                  footer=footer)
