import * as legends from './legends';
import * as widgets from './widgets';
import * as utils from './utils';
import * as errors from './errors';

export function setReady (settings) {
  try {
    onReady(settings)
  } catch (e) {
    displayError(e);
  }
}

export function onReady(settings) {
  const BASEMAPS = {
    DarkMatter: carto.basemaps.darkmatter,
    Voyager: carto.basemaps.voyager,
    Positron: carto.basemaps.positron
  };

  if (settings.mapboxtoken) {
    mapboxgl.accessToken = settings.mapboxtoken;
  }
  // Fetch CARTO basemap if it's there, else try to use other supplied style
  const map = new mapboxgl.Map({
    container: 'map',
    style: BASEMAPS[settings.basemap] || settings.basemap || {
        'version': 8,
        'sources': {},
        'layers': [{
            'id': 'background',
            'type': 'background',
            'paint': {
                'background-color': settings.basecolor
            }
        }]
    },
    zoom: 9,
    dragRotate: false
  });

  const mapInfo$ = document.getElementById('map-info');

  if (settings.show_info) {
    function updateMapInfo() {
      const center = map.getCenter();
      const lat = center.lat.toFixed(6);
      const lng = center.lng.toFixed(6);
      const zoom = map.getZoom().toFixed(2);

      mapInfo$.innerText = `viewport={'zoom': ${zoom}, 'lat': ${lat}, 'lng': ${lng}}`;
    }

    map.on('zoom', updateMapInfo);
    map.on('move', updateMapInfo);
  }

  map.fitBounds(settings.bounds, { animate: false, padding: 50, maxZoom: 14 });

  if (settings.camera) {
    map.flyTo(settings.camera);
  }

  const mapLayers = [];

  const interactiveLayers = [];
  const interactiveMapLayers = [];

  settings.layers.forEach((layer, index) => {
    const factory = new SourceFactory();
    const mapSource = factory.createSource(layer);
    const mapViz = new carto.Viz(layer['viz']);
    const mapLayer = new carto.Layer(`layer${index}`, mapSource, mapViz);

    mapLayers.push(mapLayer);

    try {
      mapLayer._updateLayer.catch(displayError);
    } catch (err) {
      throw err;
    }

    mapLayer.addTo(map);

    if (layer.interactivity) {
      interactiveLayers.push(layer);
      interactiveMapLayers.push(mapLayer);
    }

    if (settings.has_legends && layer.legend) {
      legends.createLegend(mapLayer, layer.legend, layers.length - index - 1);
    }

    if (layer.widgets.length) {
      layer.widgets.forEach((widget, widgetIndex) => {
        const id = `layer${layers.length - index - 1}_widget${widgetIndex}`;
        widget.id = id;
      });

      mapLayer.on('updated', () => {
        layer.widgets
          .filter((widget) => !widget.has_bridge)
          .forEach((widget) => {
            const value = widget.variable_name && mapLayer.viz.variables[widget.variable_name]
              ? mapLayer.viz.variables[widget.variable_name].value
              : null;

            widgets.renderWidget(widget, value);
          })
      });

      widgets.bridgeLayerWidgets(carto, mapLayer, mapSource, map, layer.widgets);
    }
  });

  if (interactiveLayers.length > 0) {
    const interactivity = new carto.Interactivity(interactiveMapLayers);
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    let clickAttrs = [];
    let hoverAttrs = [];
    interactiveLayers.forEach((interactiveLayer) => {
      interactiveLayer.interactivity.forEach((interactivityDef) => {
        if (interactivityDef.event === 'click') {
          clickAttrs = clickAttrs.concat(interactivityDef.attrs);
        } else if (interactivityDef.event === 'hover') {
          hoverAttrs = hoverAttrs.concat(interactivityDef.attrs);
        }
      });
    });

    resetPopupClick(interactivity);
    if (clickAttrs.length > 0) {
      setPopupsClick(popup, interactivity, clickAttrs);
    }

    resetPopupHover(interactivity);
    if (hoverAttrs.length > 0) {
      setPopupsHover(popup, interactivity, hoverAttrs);
    }
  }

  if (settings.default_legend) {
    legends.createDefaultLegend(mapLayers);
  }

  function updatePopup(popup, event, attrs) {
    if (event.features.length > 0) {
      let popupHTML = '';
      const layerIDs = [];

      for (const feature of event.features) {
        if (layerIDs.includes(feature.layerId)) {
          continue;
        }
        // Track layers to add only one feature per layer
        layerIDs.push(feature.layerId);
    
        for (const item of attrs) {
          const variable = feature.variables[item.name];
          if (variable) {
            let value = variable.value;
            value = utils.formatValue(value)

            popupHTML = `
              <span class="popup-name">${item.title}</span>
              <span class="popup-value">${value}</span>
            ` + popupHTML;
          }
        }
      }

      popup
          .setLngLat([event.coordinates.lng, event.coordinates.lat])
          .setHTML(`<div class="popup-content">${popupHTML}</div>`);

      if (!popup.isOpen()) {
        popup.addTo(map);
      }
    } else {
      popup.remove();
    }
  }

  function resetPopupClick(interactivity) {
    interactivity.off('featureClick');
  }

  function resetPopupHover(interactivity) {
    interactivity.off('featureHover');
  }

  function setPopupsClick(popup, interactivity, attrs) {
    interactivity.on('featureClick', (event) => {
      updatePopup(popup, event, attrs)
    });
  }

  function setPopupsHover(popup, interactivity, attrs) {
    interactivity.on('featureHover', (event) => {
      updatePopup(popup, event, attrs)
    });
  }

  function SourceFactory() {
    const sourceTypes = {
      GeoJSON: (layer) => new carto.source.GeoJSON(_decodeJSONQuery(layer.query)),
      Query: (layer) => {
        const auth = {
          username: layer.credentials['username'],
          apiKey: layer.credentials['api_key'] || 'default_public'
        };
        const config = {
          serverURL: layer.credentials['base_url'] || `https://${layer.credentials['username']}.carto.com/`
        };
        return new carto.source.SQL(layer.query, auth, config)
      },
      MVT: (layer) => new carto.source.MVT(layer.query.file, JSON.parse(layer.query.metadata)),
    }

    this.createSource = (layer) => {
      return sourceTypes[layer.type](layer);
    }
  }
}

export function displayError(e) {
  const error$ = document.getElementById('error-container');
  const errors$ = error$.getElementsByClassName('errors');
  const stacktrace$ = document.getElementById('error-stacktrace');

  errors$[0].innerHTML = e.name;
  errors$[1].innerHTML = e.name;
  errors$[2].innerHTML = e.type;
  errors$[3].innerHTML = e.message.replace(e.type, '');

  error$.style.visibility = 'visible';

  const stack = errors.parse(e.stack);
  const list = stack.map(item => {
    return `<li>
      at <span class="stacktrace-method">${item.methodName}:</span>
      (${item.file}:${item.lineNumber}:${item.column})
    </li>`;
  });

  stacktrace$.innerHTML = list.join('\n');
}

function _decodeJSONQuery(query) {
  return JSON.parse(Base64.decode(query.replace(/b\'/, '\'')))
}
