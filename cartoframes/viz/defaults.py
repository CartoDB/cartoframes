CARTO_VL_DEV = '/dist/carto-vl.js'
CARTO_VL_URL = 'https://libs.cartocdn.com/carto-vl/branches/develop/carto-vl.js'

AIRSHIP_COMPONENTS_DEV = '/packages/components/dist/airship.js'
AIRSHIP_BRIDGE_DEV = '/packages/bridge/dist/asbridge.js'
AIRSHIP_STYLE_DEV = '/packages/styles/dist/airship.css'
AIRSHIP_ICONS_DEV = '/packages/icons/dist/icons.css'
AIRSHIP_COMPONENTS_URL = 'https://libs.cartocdn.com/airship-components/cartoframes/airship.js'
AIRSHIP_BRIDGE_URL = 'https://libs.cartocdn.com/airship-bridge/cartoframes/asbridge.min.js'
AIRSHIP_STYLES_URL = 'https://libs.cartocdn.com/airship-style/cartoframes/airship.min.css'
AIRSHIP_ICONS_URL = 'https://libs.cartocdn.com/airship-icons/cartoframes/icons.css'

CREDENTIALS = {
    'username': 'cartoframes',
    'api_key': 'default_public',
    'base_url': ''
}

STYLE_PROPERTIES = [
    'color',
    'width',
    'filter',
    'strokeWidth',
    'strokeColor',
    'transform',
    'order',
    'symbol',
    'symbolPlacement',
    'resolution'
]

LEGEND_PROPERTIES = [
    'color',
    'strokeColor'
]

LEGEND_TYPES = [
    'color-category',
    'color-bins',
    'color-continuous'
]

STYLE_DEFAULTS = {
    'point': {
        'color': 'hex("#EE4D5A")',
        'width': 'ramp(linear(zoom(),0,18),[2,10])',
        'strokeWidth': 'ramp(linear(zoom(),0,18),[0,1])',
        'strokeColor': 'opacity(#222,ramp(linear(zoom(),0,18),[0,1]))'
    },
    'line': {
        'color': 'hex("#4CC8A3")',
        'width': 'ramp(linear(zoom(),0,18),[0.5,4])'
    },
    'polygon': {
        'color': 'hex("#826DBA")',
        'strokeWidth': 'ramp(linear(zoom(),2,18),[0.5,1])',
        'strokeColor': 'opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))'
    }
}
