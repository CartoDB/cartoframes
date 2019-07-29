## Basemaps And Viewport

### Viewport

By default, CARTOframes sets the center and zoom of your map to encompass all features in a dataset. In the cases where you want to modify this, you can set `show_info=True` which will place zoom and center lat/long information at the bottom left corner of your map. This information is then used to set the `viewport` of a map.

```py
from cartoframes.auth import set_default_credentials
from cartoframes.viz import Map
from cartoframes.viz.helpers import color_bins_layer

set_default_credentials('cartovl')

Map(
    color_bins_layer(
        'dallas_mkt',
        'pop_sqkm',
        'Population Density (people/sqkm)',
         bins=7,
         palette='[#20736B,#64B97A,#DFF873]'
    ),
    show_info=True
)
```

The map below symbolizes county-wide population density in Dallas County, Texas. Instead of using the default extent of the entire county, let's set the focus to the City of Dallas, Texas and surrounding areas.

The zoom and lat/long coordinate information will be set in the `viewport` parameter. In order to get that information, we first need to add it to the map.

To do this:
- we'll add the zoom and coordinate information to the map with the option `show_info=True`
- the information will be added to the bottom-left corner of the map and is updated as the map is zoomed and panned

![Show viewport info in the bottom-left corner](../../img/guides/basemap/guide-basemaps-1.png)

Once the area of interest has been located, copy and paste the values provided by `show_info` to the `viewport` parameter to set the opening zoom and center of the map.

```py
from cartoframes.viz.helpers import color_bins_layer

Map(
    color_bins_layer(
        'dallas_mkt',
        'pop_sqkm',
        'Population Density (people/sqkm)',
         bins=7,
         palette='[#20736B,#64B97A,#DFF873]'
    ),
    viewport={'zoom': 10.99, 'lat': 32.812224, 'lng': -96.929885}
)
```

![Set the viewport in the Map](../../img/guides/basemap/guide-basemaps-2.png)

### Basemap

The default basemap, Positron comes from CARTO's suite of basemaps. They have been designed to sit in the background so the visual analysis of the most important information (the story!) can more easily come to the foreground. There are other times where you will prefer not to have a basemap, add another layer to provide the right amount of geographic context, or bring in your own!

```py
from cartoframes.auth import set_default_credentials
from cartoframes.viz import Map
from cartoframes.viz.helpers import color_category_layer

set_default_credentials('cartovl')
Map(
    color_category_layer(
        'pittsburgh_311',
        'request_type',
        'Top 311 Requests',
        top=3,
        palette='[#4ABD9A,#4A5798,#F9CA34]'
    ),
    viewport={'zoom': 12.58, 'lat': 40.429251, 'lng': -79.989408}
)
```

![Default Positron basemap](../../img/guides/basemap/guide-basemaps-3.png)

By default, CARTOframes uses CARTO's Positron basemap with labels under. The basemap can be customized to use another CARTO style (Voyager, Dark Matter), a Mapbox basemap, or a custom background color; all through the `basemap` parameter:

- A CARTO basemap (`darkmatter`, `voyager` or `positron`)

```py
Map(
    color_category_layer(
        'pittsburgh_311',
        'request_type',
        'Top 311 Requests',
        top=3,
        palette='[#4ABD9A,#4A5798,#F9CA34]'
    ),
    viewport={'zoom': 12, 'lat': 40.429251, 'lng': -79.989408},
    basemap=basemaps.darkmatter
)
```

![Darkmatter basemap](../../img/guides/basemap/guide-basemaps-4.png)

- A string color:

`basemap='lightgray'`

!['lightgray' background color as basemap](../../img/guides/basemap/guide-basemaps-5.png)

- An hexadecimal color:

`basemap='#FABADA'`

![Hexadecimal color as basemap](../../img/guides/basemap/guide-basemaps-6.png)
