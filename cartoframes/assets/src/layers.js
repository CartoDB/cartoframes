import { bridgeLayerWidgets, renderWidget } from './widgets';
import { createLegends } from './legends';
import SourceFactory from './map/SourceFactory';
import { displayError } from './errors/display';

const factory = new SourceFactory();

export function initMapLayer(layer, layerIndex, numLayers, hasLegends, map, mapIndex) {
  const mapSource = factory.createSource(layer);
  const mapViz = new carto.Viz(layer.viz);
  const mapLayer = new carto.Layer(`layer${layerIndex}`, mapSource, mapViz);
  const mapLayerIndex = numLayers - layerIndex - 1;

  try {
    mapLayer._updateLayer.catch(displayError);
  } catch (e) {
    throw e;
  }

  mapLayer.addTo(map);

  setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends);
  setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource);

  return mapLayer;
}

export function getInteractiveLayers(layers, mapLayers) {
  const interactiveLayers = [];
  const interactiveMapLayers = [];

  layers.forEach((layer, index) => {
    if (layer.interactivity) {
      interactiveLayers.push(layer);
      interactiveMapLayers.push(mapLayers[index]);
    }
  });

  return { interactiveLayers, interactiveMapLayers };
}


export function setLayerInteractivity(layer, mapLayer) {
  return layer.interactivity ?
    { interactiveLayer: layer, interactiveMapLayer: mapLayer }
    : { interactiveLayer: null, interactiveMapLayer: null };
}

export function setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends) {
  if (hasLegends && layer.legends) {
    createLegends(mapLayer, layer.legends, mapLayerIndex, mapIndex);
  }
}

export function setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource) {
  if (layer.widgets.length) {
    initLayerWidgets(layer.widgets, mapLayerIndex);
    updateLayerWidgets(layer.widgets, mapLayer);
    bridgeLayerWidgets(map, mapLayer, mapSource, layer.widgets);
  }
}

export function initLayerWidgets(widgets, mapLayerIndex) {
  widgets.forEach((widget, widgetIndex) => {
    const id = `layer${mapLayerIndex}_widget${widgetIndex}`;
    widget.id = id;
  });
}

export function updateLayerWidgets(widgets, mapLayer) {
  mapLayer.on('updated', () => renderLayerWidgets(widgets, mapLayer));
}

export function renderLayerWidgets(widgets, mapLayer) {
  const variables = mapLayer.viz.variables;

  widgets
    .filter((widget) => !widget.has_bridge)
    .forEach((widget) => {
      const name = widget.variable_name;
      const value = getWidgetValue(name, variables);
      renderWidget(widget, value);
    });
}

export function getWidgetValue(name, variables) {
  return name && variables[name] ? variables[name].value : null;
}