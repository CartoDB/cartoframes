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

export async function setReady(settings) {
  try {
    if (settings.maps) {
      return await initMaps(settings.maps);
    }
    
    return await initMap(settings);
  } catch (e) {
    displayError(e);
  }
}

export async function saveImage() {
  const $image = document.getElementById('map-image');
  const $container = document.getElementById('map-container');

  html2canvas($container)
    .then((canvas) => {
      document.body.removeChild($container);
      $image.setAttribute('src', canvas.toDataURL());
      $image.style.display = 'block';
    });
}

export async function initMaps(maps) {
  return await maps.map(async function (mapSettings, mapIndex) {
    return await initMap(mapSettings, mapIndex);
  });
}

export async function initMap(settings, mapIndex) {
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

  return await initLayers(map, settings);
}

async function initLayers(map, settings) {
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

  // return new Promise((resolve) => {
  //   carto.on('loaded', mapLayers, () => {
  //       resolve(mapLayers);
  //   });
  // });
  return Promise.resolve(mapLayers);
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