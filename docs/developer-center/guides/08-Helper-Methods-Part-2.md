## Helper Methods - Part 2

There are times when you need to style a map quickly to visualize patterns during data science workflows. CARTOframes provides a set of built-in helper methods so you can make visualizations more quickly.

These predefined layer-level style helpers provide the following defaults:
- a map style based on the kind of attribute (number or category) and map type you want to make
- an appropriate legend 
- and hover interactivity on the mapped attribute

Each component of these helpers have parameters that you can accesse to customize pieces of your visualization.

In this notebook, you will see how to modify the default visualization parameters of helper methods. For a more in-depth look at each helper method, visit **CARTOframes Helper Methods: Part 1**.

### Color helper methods parameters

Let's explore what parameters are available to customize for each color-based helper method. 

#### `color_category_layer`
For the color category helper, you can customize the number of `top` category features you want to display, as well as the categorical color `palette`. Learn more about the [`top` expression](https://carto.com/developers/carto-vl/reference/#cartoexpressionstop) and [supported color values](https://carto.com/developers/carto-vl/guides/data-driven-visualizations-part-2/#color-values).

**Basic syntax**:

```
Map(
    color_category_layer('table_name', 'category_attribute', 'legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    color_category_layer('table_name', 'category_attribute', 'legend/hover title', top=11, palette='bold')
)
```


#### `color_bins_layer`
For the color bins helper, you can customize the number of classification `bins` and the sequential color `palette`.

**Basic syntax**:

```
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title', bins=5, palette='purpor')
)
```
  
#### `color_continuous_layer`
For the color continuous helper, you can customize the sequential color palette.

**Basic syntax**:

```
Map(
    color_continuous_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    color_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title', palette='sunset')
)
```

### Size helper methods parameters

Let's explore what parameters are available to customize for each size-based helper method. 


#### `size_category_layer`

For the size category helper, you can customize the number of `top` category features you want to display. Learn more about the [`top` expression](https://carto.com/developers/carto-vl/reference/#cartoexpressionstop).

**Basic syntax**:

```
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title', top=11, size='[10, 100]', color='blue')
)
```

It is possible to customize the default classification and instead of using `top`, we can use [`buckets`](https://carto.com/developers/carto-vl/reference/#cartoexpressionsbuckets) to classify a given array of categories.

```
Map(
    size_category_layer('table_name', 'category_attribute', 'legend/hover title', cat="['category_a', 'category_b']")
)
```


#### `size_bins_layer`

For the size bins helper, you can customize the number of classification `bins`, the size, and the color.

**Basic syntax**:

```
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    color_bins_layer('table_name', 'numeric_attribute','legend/hover title', bins=5, size="[10, 100]", color='blue')
)
```
  
#### `size_continuous_layer`

For the size continuous helper, you can customize the size and the color

**Basic syntax**:

```
Map(
    size_continuous_layer('table_name', 'numeric_attribute','legend/hover title')
)
```

**Access customization parameters**:

```
Map(
    size_continuous_layer('table_name', 'numeric_attribute', 'legend/hover title', size='[10, 100]', color='blue')
)
```