from ..style import Style


def basic_style(color=None, size=None, opacity=None, stroke_color=None, stroke_width=None, geom_type=None):
    """Helper function for quickly creating a layer with the basic style
    """

    default_style = {
        'point': {
            'color': color if color else 'hex("#EE4D5A")',
            'width': size if size else 'ramp(linear(zoom(),0,18),[2,10])',
            'strokeColor': stroke_color if stroke_color else 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))',
            'strokeWidth': stroke_width if stroke_width else 'ramp(linear(zoom(),0,18),[0,1])',
            'opacity': opacity if opacity else '1'
        },
        'line': {
            'color': color if color else 'hex("#4CC8A3")',
            'width': size if size else 'ramp(linear(zoom(),0,18),[0.5,4])',
            'opacity': opacity if opacity else '1'
        },
        'polygon': {
            'color': color if color else 'hex("#826DBA")',
            'strokeWidth': 'ramp(linear(zoom(),2,18),[0.5,1])',
            'strokeColor': stroke_color if stroke_color else 'opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))',
            'opacity': opacity if opacity else '0.9'
        }
    }

    return Style(default_style)
