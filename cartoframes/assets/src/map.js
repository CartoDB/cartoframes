import * as legends from './legends';
import * as widgets from './widgets';
import { displayError } from './errors/display';
import SourceFactory from './map/SourceFactory';
import { setInteractivity } from './map/interactivity';
import { updateViewport, getBasecolorSettings } from './utils';

const BASEMAPS = {
  DarkMatter: carto.basemaps.darkmatter,
  Voyager: carto.basemaps.voyager,
  Positron: carto.basemaps.positron
};

const attributionControl = new mapboxgl.AttributionControl({
  compact: false
});

const FIT_BOUNDS_SETTINGS = { animate: false, padding: 50, maxZoom: 14 };

export function setReady (settings) {
  try {
    if (settings.maps) {
      initMaps(settings.maps);
    } else {
      initMap(settings);
    }
  } catch (e) {
    displayError(e);
  }
}

export function initMaps(maps) {
  maps.forEach((mapSettings, mapIndex) => {
    initMap(mapSettings, mapIndex);
  });
}

export function initMap(settings, mapIndex) {
  const basecolor = getBasecolorSettings(settings.basecolor);
  const basemapStyle =  BASEMAPS[settings.basemap] || settings.basemap || basecolor;
  const container = mapIndex !== undefined ? `map-${mapIndex}` : 'map';
  const map = createMap(container, basemapStyle, settings.bounds, settings.mapboxtoken);

  if (settings.show_info) {
    updateViewport(map);
  }

  if (settings.camera) {
    map.flyTo(settings.camera);
  }

  initLayers(map, settings);
}

function initLayers(map, settings) {
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
    } catch (e) {
      throw e;
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
            const value = widget.variable_name && mapLayer.viz.variables[widget.variable_name] ?
              mapLayer.viz.variables[widget.variable_name].value
              : null;

            widgets.renderWidget(widget, value);
          });
      });

      widgets.bridgeLayerWidgets(carto, mapLayer, mapSource, map, layer.widgets);
    }
  });
  
  if (settings.is_static && !!settings.maps) {
    carto.on('loaded', mapLayers, () => {
      html2canvas(document.body).then(canvas => {
        document.body.appendChild(canvas);
      });
    });
  }

  if (interactiveLayers.length > 0) {
    setInteractivity(map, interactiveLayers, interactiveMapLayers);
  }

  if (settings.default_legend) {
    legends.createDefaultLegend(mapLayers);
  }
}

function createMap(container, basemapStyle, bounds, accessToken) {
  if (accessToken) {
    mapboxgl.accessToken = accessToken;
  }

  return new mapboxgl.Map({
    container,
    style: basemapStyle,
    zoom: 9,
    dragRotate: false,
    attributionControl: false
  })
  .addControl(attributionControl)
  .fitBounds(bounds, FIT_BOUNDS_SETTINGS);
}