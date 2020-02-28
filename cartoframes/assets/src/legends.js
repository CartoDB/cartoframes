import { format } from './utils';

export function createLegends(layer, legends, layerIndex, mapIndex=0) {
  if (legends.length) {
    legends.forEach((legend, legendIndex) => _createLegend(layer, legend, layerIndex, legendIndex, mapIndex));
  } else {
    _createLegend(layer, legends, layerIndex, 0, mapIndex);
  }
}

function _createLegend(layer, legend, layerIndex, legendIndex, mapIndex=0) {
  const element = document.querySelector(`#layer${layerIndex}_map${mapIndex}_legend${legendIndex}`);

  if (legend.prop) {
    const othersLabel = 'Others';   // TODO: i18n
    const prop = legend.prop;
    const dynamic = legend.dynamic;
    const order = legend.ascending ? 'ASC' : 'DESC';
    const variable = legend.variable;
    const config = { othersLabel, variable, order };
    const options = { format, config, dynamic };

    if (legend.type.startsWith('size-continuous')) {
      config.samples = 4;
    }

    AsBridge.VL.Legends.rampLegend(element, layer, prop, options);
  } else {
    // TODO: we don't have a bridge for this case, should this even be a case?
  }
}