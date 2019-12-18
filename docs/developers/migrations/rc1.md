# RC1 Migration

Migration notes from `1.0b7` to `rc1`

* [Popups](#Popups)

## Popups

* [Issue #1348](https://github.com/CartoDB/cartoframes/issues/1348)

### Hover Popup

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'hover': '$name'
    }
)
```

* To:

```python
from cartoframes.viz import Layer, hover_popup

Layer(
    'populated_places',
    popups=[
        hover_popup('name')
    ]
)
```

### Click Popup

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'click': ['$name', '$pop_max']
    }
)
```

* To:

```python
from cartoframes.viz import Layer, click_popup

Layer(
    'populated_places',
    popups=[
        click_popup('name'),
        click_popup('pop_max')
    ]
)
```

### Multiple Popups

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'hover': '$name',
        'click': ['$name', '$pop_max', '$pop_min']
    }
)
```

* To:

```python
from cartoframes.viz import Layer, click_popup, hover_popup

Layer(
    'populated_places',
    popups=[
        hover_popup('name'),
        click_popup('name'),
        click_popup('pop_max'),
        click_popup('pop_min')
    ]
)
```

### Custom Titles

* From:

```python
from cartoframes.viz import Layer

Layer(
    'populated_places'
    popup={
        'hover': {
          'value': '$name',
          'title': 'Name'
        },
        'click': [{
          'value': '$pop_max',
          'title': 'Max Population'
          },{
          'value': '$pop_min',
          'title': 'Min Population'
          }
        ]
    }
)
```

* To:

```python
from cartoframes.viz import Layer, click_popup, hover_popup

Layer(
    'populated_places',
    popups=[
        hover_popup('name', title='Name'),
        click_popup('pop_max', title='Max Population'),
        click_popup('pop_min', title='Min Population')
    ]
)
```
