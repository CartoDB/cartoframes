## Helper Methods - Part 2

There are times when you need to style a map quickly to visualize patterns during data science workflows. CARTOframes provides a set of built-in helper methods so you can make visualizations more quickly.

These predefined layer-level style helpers provide the following defaults:
- a map style based on the kind of attribute (number or category) and map type you want to make
- an appropriate legend
- and hover interactivity on the mapped attribute

Each component of these helpers have parameters that you can accesse to customize pieces of your visualization.

[Helper Methods - Part 1](https://github.com/CartoDB/cartoframes/blob/master/examples/04_helper_methods/01_helper_methods_part_1.ipynb) Notebook.

In this guide, you will see how to modify the default visualization parameters of helper methods. For a more in-depth look at each helper method, visit [Helper Methods - Part 1]({{ site.url }}/developers/cartoframes/guides/helper-methods-part-1/)

### Color helper methods parameters

Let's explore what parameters are available to customize for each color-based helper method. 

#### `color_category_layer`

For the color category helper, you can customize the number of `top` category features you want to display, as well as the categorical color `palette`. Learn more about the [`top` expression](https://carto.com/developers/carto-vl/reference/#cartoexpressionstop) and [supported color values](https://carto.com/developers/carto-vl/guides/data-driven-visualizations-part-2/#color-values).

**Basic syntax**:

```py
Map(
    color_category_layer('table_name', 'category_attribute', 'legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    color_category_layer('table_name', 'category_attribute', 'legend/hover title', top=11, palette='bold')
)
```

#### `color_bins_layer`

For the color bins helper, you can customize the number of classification `bins` and the sequential color `palette`.

**Basic syntax**:

```py
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title', bins=5, palette='purpor')
)
```
  
#### `color_continuous_layer`

For the color continuous helper, you can customize the sequential color palette.

**Basic syntax**:

```py
Map(
    color_continuous_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    color_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title', palette='sunset')
)
```

### Size helper methods parameters

Let's explore what parameters are available to customize for each size-based helper method. 

#### `size_category_layer`

For the size category helper, you can customize the number of `top` category features you want to display. Learn more about the [`top` expression](https://carto.com/developers/carto-vl/reference/#cartoexpressionstop).

**Basic syntax**:

```py
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title', top=11, size='[10, 100]', color='blue')
)
```

It is possible to customize the default classification and instead of using `top`, we can use [`buckets`](https://carto.com/developers/carto-vl/reference/#cartoexpressionsbuckets) to classify a given array of categories.

```py
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title', cat="['category_a', 'category_b']")
)
```

#### `size_bins_layer`

For the size bins helper, you can customize the number of classification `bins`, the size, and the color.

**Basic syntax**:

```py
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title', bins=5, size="[10, 100]", color='blue')
)
```
  
#### `size_continuous_layer`

For the size continuous helper, you can customize the size and the color

**Basic syntax**:

```py
Map(
    size_continuous_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```py
Map(
    size_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title', size='[10, 100]', color='blue')
)
```

### Customize visualization parameters

#### Example 1: Population Density in Dallas County

In the example below, we will modify the visualization parameters number of `bins` and `pallete` to customize a choropleth map of population density in Dallas County, Texas. 

Customizations:
- set the number of `bins` to `7` 
- custom sequential color palette (note that the three colors provided were interpolated to provide 7 colors for each class break)

```py
from cartoframes.auth import set_default_context
from cartoframes.viz import Map
from cartoframes.viz.helpers import color_bins_layer

set_default_context('https://cartovl.carto.com/')

Map(
    color_bins_layer(
        'dallas_mkt',
        'pop_sqkm',
        'Population Density (people/sqkm)',
         bins=7,
         palette='[#20736B,#64B97A,#DFF873]'
    )
)
```

![Customize Helpers - Population Density in Dallas County](../../img/guides/helper-methods-2/example-1.png)

#### Example 2: Global power plants

In the example below, `color_category_layer` visualization parameters are modified to show the top three fuel types generated by global power plants. Even though all "other" fuel type categories are grouped, the individual type categories are available on hover.

Customizations:
- set `top=3`
- custom category color palette
  - tip: you can modify the color for the "Others" default gray by overwriting it. In the example below, other values will be colored white:
    `palette='[turquoise,orange,violet],white'`

![Customize Helpers - Global power plants](../../img/guides/helper-methods-2/example-2.png)

#### Example 3: Multi-layer helpers

The example below uses different helper methods on two layers. The first is a is a `color_bins_layer` assigned to a polygon dataset and the second a `color_category_layer` assigned to point data.

Note that the top layer (`color_bins`) draws under the second (`color_category`) layer and the legends are ordered in that way too.

In order to better differentiate between both layers, and see the relationships between percent of population with a Masters degree and transaction amounts, the map below assigns a custom `palette` to the choropleth layer.

![Customize Helpers - Multi-layer](../../img/guides/helper-methods-2/example-3.png)
