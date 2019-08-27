import { format } from './utils';

export function createDefaultLegend(layers) {
  const defaultLegendContainer = document.getElementById('default-legend-container');
  defaultLegendContainer.style.display = 'none';

  AsBridge.VL.Legends.layersLegend(
    '#default-legend',
    layers,
    {
      onLoad: () => defaultLegendContainer.style.display = 'unset'
    }
  );
}

export function createLegend(layer, legendData, layerIndex, mapIndex=0) {
  const element = document.querySelector(`#layer${layerIndex}_map${mapIndex}_legend`);

  if (legendData.prop) {
    const config = { othersLabel: 'Others' };  // TODO: i18n
    const prop = legendData.prop;
    const dynamic = legendData.dynamic;
    const opts = { format, config, dynamic };

    if (legendData.type.startsWith('size-continuous')) {
      config.samples = 4;
    }
    
    AsBridge.VL.Legends.rampLegend(element, layer, prop, opts);
  } else {
    // TODO: we don't have a bridge for this case, should this even be a case?
  }
}