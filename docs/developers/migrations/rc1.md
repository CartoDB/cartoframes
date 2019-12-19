# RC1 Migration

Migration notes from `1.0b7` to `rc1`

* [Widgets](#Widgets)

## Widgets

<details><summary>Namespace</summary>
<p>

* From:

```python
from cartoframes.viz.widgets import formula_widget
```

* To:

```python
from cartoframes.viz import formula_widget
```

</p>
</details>

<details><summary>Widget class</summary>
<p>

* Don't create widgets through the `Widget` class anymore, extend the built-in widgets

</p>
</details>