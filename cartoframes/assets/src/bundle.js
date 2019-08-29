var init = (function () {
  'use strict';

  const BASEMAPS = {
    DarkMatter: carto.basemaps.darkmatter,
    Voyager: carto.basemaps.voyager,
    Positron: carto.basemaps.positron
  };

  const attributionControl = new mapboxgl.AttributionControl({
    compact: false
  });

  const FIT_BOUNDS_SETTINGS = { animate: false, padding: 50, maxZoom: 14 };

  function format(value) {
    if (Array.isArray(value)) {
      const [first, second] = value;
      if (first === -Infinity) {
        return `< ${formatValue(second)}`;
      }
      if (second === Infinity) {
        return `> ${formatValue(first)}`;
      }
      return `${formatValue(first)} - ${formatValue(second)}`;
    }
    return formatValue(value);
  }

  function formatValue(value) {
    if (typeof value === 'number') {
      return formatNumber(value);
    }
    return value;
  }

  function formatNumber(value) {
    const log = Math.log10(Math.abs(value));

    if ((log > 4 || log < -2.00000001) && value) {
      return value.toExponential(2);
    }
    
    if (!Number.isInteger(value)) {
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 3
      });
    }
    
    return value.toLocaleString();
  }

  function updateViewport(map) {
    function updateMapInfo() {
      const mapInfo$ = document.getElementById('map-info');
      const center = map.getCenter();
      const lat = center.lat.toFixed(6);
      const lng = center.lng.toFixed(6);
      const zoom = map.getZoom().toFixed(2);
    
      mapInfo$.innerText = `viewport={'zoom': ${zoom}, 'lat': ${lat}, 'lng': ${lng}}`;
    }

    updateMapInfo();

    map.on('zoom', updateMapInfo);
    map.on('move', updateMapInfo); 
  }

  function getBasecolorSettings(basecolor) {
    return {
      'version': 8,
      'sources': {},
      'layers': [{
          'id': 'background',
          'type': 'background',
          'paint': {
              'background-color': basecolor
          }
      }]
    };
  }

  function getImageElement(mapIndex) {
    const id = mapIndex !== undefined ? `map-image-${mapIndex}` : 'map-image';
    return document.getElementById(id);
  }

  function getContainerElement(mapIndex) {
    const id = mapIndex !== undefined ? `main-container-${mapIndex}` : 'main-container';
    return document.getElementById(id);
  }

  function saveImage(mapIndex) {
    const img = getImageElement(mapIndex);
    const container = getContainerElement(mapIndex);

    html2canvas(container)
      .then((canvas) => setMapImage(canvas, img, container));
  }

  function setMapImage(canvas, img, container) {
    const src = canvas.toDataURL();
    img.setAttribute('src', src);
    img.style.display = 'block';
    container.style.display = 'none';
  }

  function createDefaultLegend(layers) {
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

  function createLegend(layer, legendData, layerIndex, mapIndex=0) {
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
    }
  }

  /** From https://github.com/errwischt/stacktrace-parser/blob/master/src/stack-trace-parser.js */

  /**
   * This parses the different stack traces and puts them into one format
   * This borrows heavily from TraceKit (https://github.com/csnover/TraceKit)
   */

  const UNKNOWN_FUNCTION = '<unknown>';
  const chromeRe = /^\s*at (.*?) ?\(((?:file|https?|blob|chrome-extension|native|eval|webpack|<anonymous>|\/).*?)(?::(\d+))?(?::(\d+))?\)?\s*$/i;
  const chromeEvalRe = /\((\S*)(?::(\d+))(?::(\d+))\)/;
  const winjsRe = /^\s*at (?:((?:\[object object\])?.+) )?\(?((?:file|ms-appx|https?|webpack|blob):.*?):(\d+)(?::(\d+))?\)?\s*$/i;
  const geckoRe = /^\s*(.*?)(?:\((.*?)\))?(?:^|@)((?:file|https?|blob|chrome|webpack|resource|\[native).*?|[^@]*bundle)(?::(\d+))?(?::(\d+))?\s*$/i;
  const geckoEvalRe = /(\S+) line (\d+)(?: > eval line \d+)* > eval/i;

  function parse(stackString) {
    const lines = stackString.split('\n');

    return lines.reduce((stack, line) => {
      const parseResult =
        parseChrome(line) ||
        parseWinjs(line) ||
        parseGecko(line);

      if (parseResult) {
        stack.push(parseResult);
      }

      return stack;
    }, []);
  }

  function parseChrome(line) {
    const parts = chromeRe.exec(line);

    if (!parts) {
      return null;
    }

    const isNative = parts[2] && parts[2].indexOf('native') === 0; // start of line
    const isEval = parts[2] && parts[2].indexOf('eval') === 0; // start of line

    const submatch = chromeEvalRe.exec(parts[2]);
    if (isEval && submatch != null) {
      // throw out eval line/column and use top-most line/column number
      parts[2] = submatch[1]; // url
      parts[3] = submatch[2]; // line
      parts[4] = submatch[3]; // column
    }

    return {
      file: !isNative ? parts[2] : null,
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: isNative ? [parts[2]] : [],
      lineNumber: parts[3] ? +parts[3] : null,
      column: parts[4] ? +parts[4] : null,
    };
  }

  function parseWinjs(line) {
    const parts = winjsRe.exec(line);

    if (!parts) {
      return null;
    }

    return {
      file: parts[2],
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: [],
      lineNumber: +parts[3],
      column: parts[4] ? +parts[4] : null,
    };
  }

  function parseGecko(line) {
    const parts = geckoRe.exec(line);

    if (!parts) {
      return null;
    }

    const isEval = parts[3] && parts[3].indexOf(' > eval') > -1;

    const submatch = geckoEvalRe.exec(parts[3]);
    if (isEval && submatch != null) {
      // throw out eval line/column and use top-most line number
      parts[3] = submatch[1];
      parts[4] = submatch[2];
      parts[5] = null; // no column when eval
    }

    return {
      file: parts[3],
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: parts[2] ? parts[2].split(',') : [],
      lineNumber: parts[4] ? +parts[4] : null,
      column: parts[5] ? +parts[5] : null,
    };
  }

  function displayError(e) {
    const error$ = document.getElementById('error-container');
    const errors$ = error$.getElementsByClassName('errors');
    const stacktrace$ = document.getElementById('error-stacktrace');

    errors$[0].innerHTML = e.name;
    errors$[1].innerHTML = e.name;
    errors$[2].innerHTML = e.type;
    errors$[3].innerHTML = e.message.replace(e.type, '');

    error$.style.visibility = 'visible';

    const stack = parse(e.stack);
    const list = stack.map(item => {
      return `<li>
      at <span class="stacktrace-method">${item.methodName}:</span>
      (${item.file}:${item.lineNumber}:${item.column})
    </li>`;
    });

    stacktrace$.innerHTML = list.join('\n');
  }

  function resetPopupClick(interactivity) {
    interactivity.off('featureClick');
  }

  function resetPopupHover(interactivity) {
    interactivity.off('featureHover');
  }

  function setPopupsClick(map, popup, interactivity, attrs) {
    interactivity.on('featureClick', (event) => {
      updatePopup(map, popup, event, attrs);
    });
  }

  function setPopupsHover(map, popup, interactivity, attrs) {
    interactivity.on('featureHover', (event) => {
      updatePopup(map, popup, event, attrs);
    });
  }

  function updatePopup(map, popup, event, attrs) {
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
            value = formatValue(value);

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

  function setInteractivity(map, interactiveLayers, interactiveMapLayers) {
    const interactivity = new carto.Interactivity(interactiveMapLayers);
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    const { clickAttrs, hoverAttrs } = _setInteractivityAttrs(interactiveLayers);

    resetPopupClick(map);
    resetPopupHover(map);

    if (clickAttrs.length > 0) {
      setPopupsClick(map, popup, interactivity, clickAttrs);
    }

    if (hoverAttrs.length > 0) {
      setPopupsHover(map, popup, interactivity, hoverAttrs);
    }
  }

  function _setInteractivityAttrs(interactiveLayers) {
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

    return { clickAttrs, hoverAttrs };
  }

  function renderWidget(widget, value) {
    widget.element = widget.element || document.querySelector(`#${widget.id}-value`);

    if (value && widget.element) {
      widget.element.innerText = typeof value === 'number' ? format(value) : value;
    }
  }

  function renderBridge(bridge, widget, mapLayer) {
    widget.element = widget.element || document.querySelector(`#${widget.id}`);
    const type = mapLayer.metadata.properties[widget.value].type;

    switch (widget.type) {
      case 'histogram':
        const histogram = type === 'category' ? 'categoricalHistogram' : 'numericalHistogram';
        bridge[histogram](widget.element, widget.value, widget.options);

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

  function bridgeLayerWidgets(map, mapLayer, mapSource, widgets) {
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

  function SourceFactory() {
    const sourceTypes = { GeoJSON, Query, MVT };

    this.createSource = (layer) => {
      return sourceTypes[layer.type](layer);
    };
  }

  function GeoJSON(layer) {
    return new carto.source.GeoJSON(_decodeJSONQuery(layer.query));
  }

  function Query(layer) {
    const auth = {
      username: layer.credentials.username,
      apiKey: layer.credentials.api_key || 'default_public'
    };

    const config = {
      serverURL: layer.credentials.base_url || `https://${layer.credentials.username}.carto.com/`
    };

    return new carto.source.SQL(layer.query, auth, config);
  }

  function MVT(layer) {
    return new carto.source.MVT(layer.query.file, JSON.parse(layer.query.metadata));
  }

  function _decodeJSONQuery(query) {
    return JSON.parse(Base64.decode(query.replace(/b\'/, '\'')));
  }

  const factory = new SourceFactory();

  function initMapLayer(layer, layerIndex, numLayers, hasLegends, map, mapIndex) {
    const mapSource = factory.createSource(layer);
    const mapViz = new carto.Viz(layer.viz);
    const mapLayer = new carto.Layer(`layer${layerIndex}`, mapSource, mapViz);
    const mapLayerIndex = numLayers - layerIndex - 1;

    try {
      mapLayer._updateLayer.catch(displayError);
    } catch (e) {
      throw e;
    }

    setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends);
    setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource);

    mapLayer.addTo(map);

    return mapLayer;
  }

  function getInteractiveLayers(layers, mapLayers) {
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

  function setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends) {
    if (hasLegends && layer.legend) {
      createLegend(mapLayer, layer.legend, mapLayerIndex, mapIndex);
    }
  }

  function setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource) {
    if (layer.widgets.length) {
      initLayerWidgets(layer.widgets, mapLayerIndex);
      updateLayerWidgets(layer.widgets, mapLayer);
      bridgeLayerWidgets(map, mapLayer, mapSource, layer.widgets);
    }
  }

  function initLayerWidgets(widgets, mapLayerIndex) {
    widgets.forEach((widget, widgetIndex) => {
      const id = `layer${mapLayerIndex}_widget${widgetIndex}`;
      widget.id = id;
    });
  }

  function updateLayerWidgets(widgets, mapLayer) {
    mapLayer.on('updated', () => renderLayerWidgets(widgets, mapLayer));
  }

  function renderLayerWidgets(widgets, mapLayer) {
    const variables = mapLayer.viz.variables;

    widgets
      .filter((widget) => !widget.has_bridge)
      .forEach((widget) => {
        const name = widget.variable_name;
        const value = getWidgetValue(name, variables);
        renderWidget(widget, value);
      });
  }

  function getWidgetValue(name, variables) {
    return name && variables[name] ? variables[name].value : null;
  }

  function setReady(settings) {
    try {
      return settings.maps ? initMaps(settings.maps) : initMap(settings);
    } catch (e) {
      displayError(e);
    }
  }

  function initMaps(maps) {
    return maps.map((mapSettings, mapIndex) => {
      return initMap(mapSettings, mapIndex);
    });
  }

  function initMap(settings, mapIndex) {
    const basecolor = getBasecolorSettings(settings.basecolor);
    const basemapStyle =  BASEMAPS[settings.basemap] || settings.basemap || basecolor;
    const container = mapIndex !== undefined ? `map-${mapIndex}` : 'map';
    const map = createMap(container, basemapStyle, settings.bounds, settings.mapboxtoken);

    console.log('!!! settings', settings);

    if (settings.show_info) {
      updateViewport(map);
    }

    if (settings.camera) {
      map.flyTo(settings.camera);
    }

    return initLayers(map, settings, mapIndex);
  }

  function initLayers(map, settings, mapIndex) {
    const numLayers = settings.layers.length;
    const hasLegends = settings.has_legends;
    const isDefaultLegend = settings.default_legend;
    const isStatic = settings.is_static;
    const layers = settings.layers;
    const mapLayers = getMapLayers(
      layers,
      numLayers,
      hasLegends,
      map,
      mapIndex
    );

    createLegend$1(isDefaultLegend, mapLayers);
    setInteractiveLayers(map, layers, mapLayers);

    return waitForMapLayersLoad(isStatic, mapIndex, mapLayers);
  }

  function waitForMapLayersLoad(isStatic, mapIndex, mapLayers) {
    return new Promise((resolve) => {
      carto.on('loaded', mapLayers, onMapLayersLoaded.bind(
        this, isStatic, mapIndex, mapLayers, resolve)
      );
    });
  }

  function onMapLayersLoaded(isStatic, mapIndex, mapLayers, resolve) {
    if (isStatic) {
      saveImage(mapIndex);
    }

    resolve(mapLayers);
  }

  function getMapLayers(layers, numLayers, hasLegends, map, mapIndex) {
    return layers.map((layer, layerIndex) => {
      return initMapLayer(layer, layerIndex, numLayers, hasLegends, map, mapIndex);
    });
  }

  function setInteractiveLayers(map, layers, mapLayers) {
    const { interactiveLayers, interactiveMapLayers } = getInteractiveLayers(layers, mapLayers);

    if (interactiveLayers && interactiveLayers.length > 0) {
      setInteractivity(map, interactiveLayers, interactiveMapLayers);
    }
  }

  function createLegend$1(isDefaultLegend, mapLayers) {
    if (isDefaultLegend) {
      createDefaultLegend(mapLayers);
    }
  }

  function createMap(container, basemapStyle, bounds, accessToken) {
    const map = createMapboxGLMap(container, basemapStyle, accessToken);

    map.addControl(attributionControl);
    map.fitBounds(bounds, FIT_BOUNDS_SETTINGS);

    return map;
  }

  function createMapboxGLMap(container, style, accessToken) {
    if (accessToken) {
      mapboxgl.accessToken = accessToken;
    }

    return new mapboxgl.Map({
      container,
      style,
      zoom: 9,
      dragRotate: false,
      attributionControl: false
    });
  }

  function init(settings) {
    setReady(settings);
  }

  return init;

}());
