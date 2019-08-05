import * as legends from './legends';
import * as widgets from './widgets';
import { displayError } from './errors/display';
import SourceFactory from './map/SourceFactory';
import { setInteractivity } from './map/interactivity';

export function setReady (settings) {
  try {
    onReady(settings);
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

  const BASECOLOR = {
    'version': 8,
    'sources': {},
    'layers': [{
        'id': 'background',
        'type': 'background',
        'paint': {
            'background-color': settings.basecolor
        }
    }]
  };

  if (settings.mapboxtoken) {
    mapboxgl.accessToken = settings.mapboxtoken;
  }

  const basemapStyle =  BASEMAPS[settings.basemap] || settings.basemap || BASECOLOR;

  const map = new mapboxgl.Map({
    container: 'map',
    style: basemapStyle,
    zoom: 9,
    dragRotate: false
  });

  map.fitBounds(settings.bounds, { animate: false, padding: 50, maxZoom: 14 });

  if (settings.show_info) {
    const updateMapInfo = _updateMapInfo.bind(this, map);

    map.on('zoom', updateMapInfo);
    map.on('move', updateMapInfo);
  }

  if (settings.camera) {
    map.flyTo(settings.camera);
  }

  const mapLayers = [];
  const interactiveLayers = [];
  const interactiveMapLayers = [];
  const factory = new SourceFactory();

  settings.layers.forEach((layer, index) => {
    const mapSource = factory.createSource(layer);
    const mapViz = new carto.Viz(layer.viz);
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
      legends.createLegend(mapLayer, layer.legend, settings.layers.length - index - 1);
    }

    if (layer.widgets.length) {
      layer.widgets.forEach((widget, widgetIndex) => {
        const id = `layer${settings.layers.length - index - 1}_widget${widgetIndex}`;
        widget.id = id;
      });

      mapLayer.on('updated', () => {
        layer.widgets
          .filter((widget) => !widget.has_bridge)
          .forEach((widget) => {
            const value = widget.variable_name && mapLayer.viz.variables[widget.variable_name] ?
              mapLayer.viz.variables[widget.variable_name].value
              : null;

            widgets.renderWidget(widget, value);
          });
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

function _updateMapInfo(map) {
  const mapInfo$ = document.getElementById('map-info');

  const center = map.getCenter();
  const lat = center.lat.toFixed(6);
  const lng = center.lng.toFixed(6);
  const zoom = map.getZoom().toFixed(2);

  mapInfo$.innerText = `viewport={'zoom': ${zoom}, 'lat': ${lat}, 'lng': ${lng}}`;
}