CARTO_VL_VERSION = 'v1.4'
CARTO_VL_DEV = '/dist/carto-vl.js'
CARTO_VL_URL = 'https://libs.cartocdn.com/carto-vl/{}/carto-vl.min.js'.format(CARTO_VL_VERSION)

AIRSHIP_VERSION = 'v2.2.0-rc.2'
AIRSHIP_COMPONENTS_DEV = '/packages/components/dist/airship.js'
AIRSHIP_BRIDGE_DEV = '/packages/bridge/dist/asbridge.js'
AIRSHIP_MODULE_DEV = '/packages/components/dist/airship/airship.esm.js'
AIRSHIP_STYLES_DEV = '/packages/styles/dist/airship.css'
AIRSHIP_ICONS_DEV = '/packages/icons/dist/icons.css'
AIRSHIP_COMPONENTS_URL = 'https://libs.cartocdn.com/airship-components/{}/airship.js'.format(AIRSHIP_VERSION)
AIRSHIP_BRIDGE_URL = 'https://libs.cartocdn.com/airship-bridge/{}/asbridge.min.js'.format(AIRSHIP_VERSION)
AIRSHIP_MODULE_URL = 'https://libs.cartocdn.com/airship-components/{}/airship/airship.esm.js'.format(AIRSHIP_VERSION)
AIRSHIP_STYLES_URL = 'https://libs.cartocdn.com/airship-style/{}/airship.min.css'.format(AIRSHIP_VERSION)
AIRSHIP_ICONS_URL = 'https://libs.cartocdn.com/airship-icons/{}/icons.css'.format(AIRSHIP_VERSION)

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
    'strokeColor',
    'width',
    'strokeWidth'
]

LEGEND_TYPES = [
    'color-bins',
    'color-bins-line',
    'color-bins-point',
    'color-bins-polygon',
    'color-category',
    'color-category-line',
    'color-category-point',
    'color-category-polygon',
    'color-continuous',
    'color-continuous-line',
    'color-continuous-point',
    'color-continuous-polygon',
    'size-bins',
    'size-bins-line',
    'size-bins-point',
    'size-category',
    'size-category-line',
    'size-category-point',
    'size-continuous',
    'size-continuous-line',
    'size-continuous-point'
]

WIDGET_TYPES = [
    'default',
    'formula',
    'histogram',
    'category',
    'animation',
    'time-series'
]

FORMULA_OPERATIONS_VIEWPORT = {
  'count': 'viewportCount',
  'avg': 'viewportAvg',
  'min': 'viewportMin',
  'max': 'viewportMax',
  'sum': 'viewportSum'
}

FORMULA_OPERATIONS_GLOBAL = {
  'count': 'globalCount',
  'avg': 'globalAvg',
  'min': 'globalMin',
  'max': 'globalMax',
  'sum': 'globalSum'
}
THEMES = ['dark', 'light']
