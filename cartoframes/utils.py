import sys

def dict_items(d):
    if sys.version_info >= (3,0):
        return d.items()
    else:
        return d.iteritems()

def cssify(css_dict):
    css = ''
    for key, value in dict_items(css_dict):
        css += '{key} {{ '.format(key=key)
        for field, field_value in dict_items(value):
            css += ' {field}: {field_value};'.format(field=field,
                                                     field_value=field_value)
        css += '} '
    return css
