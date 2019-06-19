## Helper Methods - Part 1

There are times when you need to style a map quickly to visualize patterns during data science workflows. CARTOframes provides a set of built-in helper methods so you can make visualizations more quickly.

These predefined layer-level style helpers provide the following defaults:
- a map style based on the kind of attribute (number or category) and map type you want to make
- an appropriate legend
- hover interactivity on the mapped attribute

[Helper Methods - Part 1](https://github.com/CartoDB/cartoframes/blob/develop/examples/04_helper_methods/01_helper_methods_part_1.ipynb) Notebook.

Each component of these helpers (Map, Style, Legend, Popup) have parameters that you can be accessed to customize your visualization which will be covered in [Helper Methods - Part 2]({{ site.url }}/developers/cartoframes/guides/helper-methods-part-2/)

### Helper methods

There is a common pattern to all visualization-based helper method defaults:

```py
Map(
    helper_method_layer('source_data', 'symbolizing_attribute','legend/hover title')
)
```

Each parameter will be discussed in more detail in the following section in the context of different CARTOframes layer methods.

_**Note**_:
_While not covered in this guide, the parameter source data refers to the data that you want to interact with and visualize in your data science workflow. CARTOframes accepts multiple source layer formats including Dataset, SQL query, mutliple GeoJSON formats including geopandas GeoDataFrame._

## Helper methods: color

### `color_category_layer`

**Visualization defaults**:

For use with **categorical** attributes of any geometry (point, line, polygon) type. By default, the top `11` categories in your data are assigned a color and all other categories are bucketed into an "Others" category. If there are fewer than `11` categories, all categories will be colored and no "Others" bucket will appear. This helper uses the categorical CARTOColor scheme `bold`.

**Legend and hover defaults**:

The legend lists and labels each of the categories that are symbolized on the map. The legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    color_category_layer('table_name', 'category_attribute','legend/hover title')
)
```

**Examples**:

![color-category-point Legend](../../img/guides/helper-methods-1/color-category-point.png)
![color-category-line Legend](../../img/guides/helper-methods-1/color-category-line.png)
![color-category-polygon Legend](../../img/guides/helper-methods-1/color-category-polygon.png)

### `color_bins_layer`

**Visualization defaults**:

For use with **numeric** data. Use this method to create a classed map. By default, this method classifies your numeric data using `globalQuantiles` with `5` class breaks. This helper uses the sequential CARTOColor scheme `purpor`.

**Legend and hover defaults**:

The legend lists and labels each of the five bins and range of values that are symbolized on the map. Similar to other methods, the legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    color_bins_layer('table_name', 'numeric_attribute', 'legend/hover title')
)
```

**Examples**:

![color-bins-point Legend](../../img/guides/helper-methods-1/color-bins-point.png)
![color-bins-line Legend](../../img/guides/helper-methods-1/color-bins-line.png)
![color-bins-polygon Legend](../../img/guides/helper-methods-1/color-bins-polygon.png)

  
### `color_continuous_layer`

**Visualization defaults**:

For use with **numeric** data. Use this method to map a continuous range of numeric data to a continuous range of colors. This method uses the sequential CARTOColor scheme `sunset`.

**Legend and hover defaults**:

The legend lists and labels each breakpoint of the continuous values that are symbolized with the associated color on the map. Similar to other methods, the legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    color_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title')
)
```

**Examples**:

![color-continuous-point Legend](../../img/guides/helper-methods-1/color-continuous-point.png)
![color-continuous-line Legend](../../img/guides/helper-methods-1/color-continuous-line.png)
![color-continuous-polygon Legend](../../img/guides/helper-methods-1/color-continuous-polygon.png)

## Helper methods: size

### `size_category_layer`

**Visualization defaults**:

For use with **categorical** attributes of any point or line geometry type. By default, the top `5` categories in your data are assigned a color and all other categories are bucketed into an "Others" category. If there are fewer than `5` categories, all categories will be colored and no "Others" bucket will appear.
This helper uses the a size range between `2` and `20` for points and between `1` and `10` for lines.

**Legend and hover defaults**:

The legend lists and labels each of the categories that are symbolized on the map. The legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    size_category_layer('table_name', 'category_attribute','legend/hover title')
)
```

**Examples**:

![size-category-point Legend](../../img/guides/helper-methods-1/size-category-point.png)
![size-category-line Legend](../../img/guides/helper-methods-1/size-category-line.png)

### `size_bins_layer`

**Visualization defaults**:

For use with **numeric** data. Use this method to create a classed map. By default, this method classifies your numeric data using `globalQuantiles` with `5` class breaks. This helper uses the a size range between `2` and `20` for points and between `1` and `10` for lines.

**Legend and hover defaults**:

The legend lists and labels each of the five bins and range of values that are symbolized on the map. Similar to other methods, the legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    size_bins_layer('table_name', 'numeric_attribute', 'legend/hover title')
)
```

**Examples**:

![size-bins-point Legend](../../img/guides/helper-methods-1/size-bins-point.png)
![size-bins-line Legend](../../img/guides/helper-methods-1/size-bins-line.png)
  
### `size_continuous_layer`

**Visualization defaults**:

For use with **numeric** data. Use this method to map a continuous range of numeric data to a continuous range of colors. By default, this method classifies your numeric data using `linear` with the square root of the value provided. For points, the `linear` function goes from the square root of the minimum value to the square root of the maximum value for points. This helper uses the a size range between `2` and `20` for points and between `1` and `10` for lines.

**Legend and hover defaults**:

The legend lists and labels each breakpoint of the continuous values that are symbolized with the associated color on the map. Similar to other methods, the legend title can be customized with the third parameter of the definition (see below). If no title is provided, it will default to the attribute name being mapped. The hover title is inherited from title and/or defaults to the attribute name being mapped. Each features value is also displayed when hovered.

**Basic syntax**:

```py
Map(
    size_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title')
)
```

**Examples**:

![size-continuous-point Legend](../../img/guides/helper-methods-1/size-continuous-point.png)
![size-continuous-line Legend](../../img/guides/helper-methods-1/size-continuous-line.png)
