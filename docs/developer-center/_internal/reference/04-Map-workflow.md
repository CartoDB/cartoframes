### Map workflow

The following will embed a CARTO map in a Jupyter notebook, allowing for custom styling of the maps driven by [TurboCARTO](https://github.com/CartoDB/turbo-carto) and [CARTOColors](https://carto.com/blog/introducing-cartocolors). See the [CARTOColors wiki](https://github.com/CartoDB/CartoColor/wiki/CARTOColor-Scheme-Names) for a full list of available color schemes.

```python
from cartoframes import Layer, BaseMap, styling
cc = cartoframes.CartoContext(base_url=BASEURL,
                              api_key=APIKEY)
cc.map(layers=[BaseMap('light'),
               Layer('acadia_biodiversity',
                     color={'column': 'simpson_index',
                            'scheme': styling.tealRose(5)}),
               Layer('peregrine_falcon_nest_sites',
                     size='num_eggs',
                     color={'column': 'bird_id',
                            'scheme': styling.vivid(10)})],
       interactive=True)
 ```

![../../img/map_demo.gif](https://raw.githubusercontent.com/CartoDB/cartoframes/master/docs/map_demo.gif)

**Note**

Legends are under active development. See [https://github.com/CartoDB/cartoframes/pull/184](https://github.com/CartoDB/cartoframes/pull/184) for more information. To try out that code, install cartoframes as:

```bash
$ pip install git+https://github.com/cartodb/cartoframes.git@add-legends-v1#egg=cartoframes
```
