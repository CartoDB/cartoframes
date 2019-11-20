# [Guide Title]

## Introduction

The introduction to the guide goes here. It should say what the purpose is and the main topics it covers.
In some cases it's possible to highlight here the **final result** you'll have learnt when finishing the guide.

## [Data Used] (*optional*)

- [Dataset 1 Name](dataset_link): Dataset description
- [Dataset 2 Name](dataset_link): Dataset description

## [Section 1 Title]

Explain what the Section 1 covers.

To embed maps, use this iframe inside an `"example-map"` div container. Set a unique `id` as an attribute and assign your published map link in the `src` attribute.

```html
<div class="example-map">
    <iframe
        id="unique-ide"
        src="map-link-url"
        width="100%"
        height="500"
        style="margin: 20px auto !important"
        frameBorder="0">
    </iframe>
</div>
```

To add a link to the **reference** section, use the same namespace you'll use for any class or method in CARTOframes, but using dashes instead of dots. For example, `cartoframes.data.observatory.Category` is `cartoframes-data-observatory-Category`:

To add a link to an **example**:

```
  [Data Observatory - Category](/developers/cartoframes/reference/#cartoframes-data-observatory-Category)
```

## [Section n Title]

Explain what the Section n covers.

## Conclusion

Explain the guide results, conclusions or main topics to enhance them.