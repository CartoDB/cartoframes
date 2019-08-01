import * as legends from './legends';
import * as widgets from './widgets';
import * as utils from './utils';
import { displayError } from './errors/display';
import SourceFactory from './map/SourceFactory';
import { setInteractivity } from './map/interactivity';

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
    setInteractivity(map, interactiveLayers, interactiveMapLayers);
  }

  if (settings.default_legend) {
    legends.createDefaultLegend(mapLayers);
  }
}