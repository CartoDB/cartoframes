import pandas as pd
import geopandas as gpd

from shapely import wkb

from ....utils.utils import check_package
from ....utils.logger import log


def variable_describe(data):
    if not data or not data.get('stats'):
        return

    stats = dict(data.get('stats'))
    stats.update(data.get('quantiles'))

    return pd.Series(stats)


def dataset_describe(variables):
    describe = dict()

    for variable in variables:
        if variable.describe() is None:
            continue

        describe[variable.column_name] = variable.describe()

    return pd.DataFrame.from_dict(describe)


def head(cls, data):
    from .dataset import Dataset
    from .variable import Variable

    if not data:
        return

    if cls == Variable:
        head = pd.Series(data['head'])
    elif cls == Dataset:
        head = pd.DataFrame(data['glimpses']['head'])

    return head


def tail(cls, data):
    from .dataset import Dataset
    from .variable import Variable

    if not data:
        return

    if cls == Variable:
        tail = pd.Series(data['tail'])
    elif cls == Dataset:
        tail = pd.DataFrame(data['glimpses']['tail'])

    return tail


def counts(data):
    if not data:
        return
    return pd.Series(data['counts'])


def quantiles(data):
    if not data:
        return
    return pd.Series(data['quantiles'])


def top_values(data):
    check_package('matplotlib', is_optional=True)
    import matplotlib.pyplot as plt

    if not data:
        return

    top_values = pd.DataFrame(data['top_values'])

    position = list(reversed(range(top_values.shape[0])))

    plt.barh(position, top_values['count'], align='center', alpha=0.5)
    plt.yticks(position, top_values['value'])
    plt.xlabel('Count')
    plt.ylabel('Value')
    plt.title('Top values')

    plt.show()


def fields_by_type(data):
    if not data:
        return
    return pd.Series(data['fields_by_type'])


def geom_coverage(geography_id):
    from .geography import Geography
    from ....viz import Map, Layer

    geography = Geography.get(geography_id)

    if geography.geom_coverage:
        geom_coverage = wkb.loads(geography.geom_coverage, hex=True)
        geom_coverage_gdf = gpd.GeoDataFrame({'geometry': [geom_coverage]}, geometry='geometry')
        return Map(Layer(geom_coverage_gdf))
    else:
        log.info('Geometry coverage not available')


def histogram(data):
    check_package('matplotlib', is_optional=True)
    import matplotlib.pyplot as plt

    range_element = [round(element['min_range'], 2) for element in data['histogram']]
    count = [element['count'] for element in data['histogram']]

    count_normalized = [element/sum(count) for element in count]

    position = list(range(len(range_element)))
    plt.figure(figsize=(12, 7))
    plt.bar(position, count_normalized, align='center', alpha=0.5, width=abs(position[1] - position[0]))
    plt.xticks(position, range_element)

    plt.title('Histogram')
    plt.xticks(rotation=60)
    plt.show()
