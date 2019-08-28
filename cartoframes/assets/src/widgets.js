import { format } from './utils';

export function renderWidget(widget, value) {
  widget.element = widget.element || document.querySelector(`#${widget.id}-value`);

  if (value && widget.element) {
    widget.element.innerText = typeof value === 'number' ? format(value) : value;
  }
}

export function renderBridge(bridge, widget, mapLayer) {
  widget.element = widget.element || document.querySelector(`#${widget.id}`);
  const type = mapLayer.metadata.properties[widget.value].type;

  console.log('!!! renderBridge', widget);

  switch (widget.type) {
    case 'histogram':
      if (type === 'category') {
        bridge.categoricalHistogram(widget.element, widget.value, widget.options);
      } else {
        bridge.numericalHistogram(widget.element, widget.value, widget.options);
      }

      break;
    case 'category':
      bridge.category(widget.element, widget.value, widget.options);
      break;
    case 'animation':
      widget.options.propertyName = widget.prop;
      bridge.animationControls(widget.element, widget.value, widget.options);
      break;
    case 'time-series':
      widget.options.propertyName = widget.prop;
      bridge.timeSeries(widget.element, widget.value, widget.options);
      break;
  }
}

export function bridgeLayerWidgets(map, mapLayer, mapSource, widgets) {
  const bridge = new AsBridge.VL.Bridge({
    carto: carto,
    layer: mapLayer,
    source: mapSource,
    map: map
  });

  mapLayer.on('loaded', () => {
    widgets
      .filter((widget) => widget.has_bridge)
      .forEach((widget) => renderBridge(bridge, widget, mapLayer));

    bridge.build();
  });
}
