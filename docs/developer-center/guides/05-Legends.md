## Legends

There are different types of legends we can use in our visualization. These legends depend on the geometry of the layer and on the type of the data it is being represented.

### Legend Types

When we set the legend, we have to indicate the type of the legend. Current types are:

* Color
  * `color-category`
  * `color-bins`
  * `color-continuous`

* Size
  * `size-category`
  * `size-bins`
  * `size-continuous`

#### Classified by property

As we can see in the previous list of legend types, there're two types of legend regarding style: **color** and **size**. 

* **Color** types represent color style properties: `color` and `strokeColor`.
* **Size** types represent size style properties: `width` and `strokeWidth`.

#### Classified by data type

Each color and size legend legend types have three options: **category**, **bins**, and **continuous**.

* **Category** legends: for use with **categorical** data.
* **Bins** legends: for use with **numeric** data.
* **Continuous** legends: for use with **numeric** data.

By default, each of the previous types detects the geometry of the layer. However, we set explicitely the geometry, which is very useful when having several legens to identify the each one type.

### Default Legend

```py
Map(
    Layer('populated_places'),
    default_legend=True
)
```

### Color Category
  * color-category-point
  * color-category-line
  * color-category-polygon

### Color Bins
  * color-bins-point
  * color-bins-line
  * color-bins-polygon

### Color Continuous
  * color-continuous-point
  * color-continuous-line
  * color-continuous-polygon

### Size Category
  * size-category-point
  * size-category-line

### Size Bins
  * size-bins-point
  * size-bins-line

### Size Continuous
  * size-continuous-point
  * size-continuous-line

## Multiple Legends