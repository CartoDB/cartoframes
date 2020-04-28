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

  const FIT_BOUNDS_SETTINGS = { animate: false, padding: 50, maxZoom: 16 };

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
    errors$[1].innerHTML = e.type;
    errors$[2].innerHTML = e.message.replace(e.type, '');

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

  // Computes the decimal coefficient and exponent of the specified number x with
  // significant digits p, where x is positive and p is in [1, 21] or undefined.
  // For example, formatDecimal(1.23) returns ["123", 0].
  function formatDecimal(x, p) {
    if ((i = (x = p ? x.toExponential(p - 1) : x.toExponential()).indexOf("e")) < 0) return null; // NaN, ±Infinity
    var i, coefficient = x.slice(0, i);

    // The string returned by toExponential either has the form \d\.\d+e[-+]\d+
    // (e.g., 1.2e+3) or the form \de[-+]\d+ (e.g., 1e+3).
    return [
      coefficient.length > 1 ? coefficient[0] + coefficient.slice(2) : coefficient,
      +x.slice(i + 1)
    ];
  }

  function exponent(x) {
    return x = formatDecimal(Math.abs(x)), x ? x[1] : NaN;
  }

  function formatGroup(grouping, thousands) {
    return function(value, width) {
      var i = value.length,
          t = [],
          j = 0,
          g = grouping[0],
          length = 0;

      while (i > 0 && g > 0) {
        if (length + g + 1 > width) g = Math.max(1, width - length);
        t.push(value.substring(i -= g, i + g));
        if ((length += g + 1) > width) break;
        g = grouping[j = (j + 1) % grouping.length];
      }

      return t.reverse().join(thousands);
    };
  }

  function formatNumerals(numerals) {
    return function(value) {
      return value.replace(/[0-9]/g, function(i) {
        return numerals[+i];
      });
    };
  }

  // [[fill]align][sign][symbol][0][width][,][.precision][~][type]
  var re = /^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;

  function formatSpecifier(specifier) {
    if (!(match = re.exec(specifier))) throw new Error("invalid format: " + specifier);
    var match;
    return new FormatSpecifier({
      fill: match[1],
      align: match[2],
      sign: match[3],
      symbol: match[4],
      zero: match[5],
      width: match[6],
      comma: match[7],
      precision: match[8] && match[8].slice(1),
      trim: match[9],
      type: match[10]
    });
  }

  formatSpecifier.prototype = FormatSpecifier.prototype; // instanceof

  function FormatSpecifier(specifier) {
    this.fill = specifier.fill === undefined ? " " : specifier.fill + "";
    this.align = specifier.align === undefined ? ">" : specifier.align + "";
    this.sign = specifier.sign === undefined ? "-" : specifier.sign + "";
    this.symbol = specifier.symbol === undefined ? "" : specifier.symbol + "";
    this.zero = !!specifier.zero;
    this.width = specifier.width === undefined ? undefined : +specifier.width;
    this.comma = !!specifier.comma;
    this.precision = specifier.precision === undefined ? undefined : +specifier.precision;
    this.trim = !!specifier.trim;
    this.type = specifier.type === undefined ? "" : specifier.type + "";
  }

  FormatSpecifier.prototype.toString = function() {
    return this.fill
        + this.align
        + this.sign
        + this.symbol
        + (this.zero ? "0" : "")
        + (this.width === undefined ? "" : Math.max(1, this.width | 0))
        + (this.comma ? "," : "")
        + (this.precision === undefined ? "" : "." + Math.max(0, this.precision | 0))
        + (this.trim ? "~" : "")
        + this.type;
  };

  // Trims insignificant zeros, e.g., replaces 1.2000k with 1.2k.
  function formatTrim(s) {
    out: for (var n = s.length, i = 1, i0 = -1, i1; i < n; ++i) {
      switch (s[i]) {
        case ".": i0 = i1 = i; break;
        case "0": if (i0 === 0) i0 = i; i1 = i; break;
        default: if (!+s[i]) break out; if (i0 > 0) i0 = 0; break;
      }
    }
    return i0 > 0 ? s.slice(0, i0) + s.slice(i1 + 1) : s;
  }

  var prefixExponent;

  function formatPrefixAuto(x, p) {
    var d = formatDecimal(x, p);
    if (!d) return x + "";
    var coefficient = d[0],
        exponent = d[1],
        i = exponent - (prefixExponent = Math.max(-8, Math.min(8, Math.floor(exponent / 3))) * 3) + 1,
        n = coefficient.length;
    return i === n ? coefficient
        : i > n ? coefficient + new Array(i - n + 1).join("0")
        : i > 0 ? coefficient.slice(0, i) + "." + coefficient.slice(i)
        : "0." + new Array(1 - i).join("0") + formatDecimal(x, Math.max(0, p + i - 1))[0]; // less than 1y!
  }

  function formatRounded(x, p) {
    var d = formatDecimal(x, p);
    if (!d) return x + "";
    var coefficient = d[0],
        exponent = d[1];
    return exponent < 0 ? "0." + new Array(-exponent).join("0") + coefficient
        : coefficient.length > exponent + 1 ? coefficient.slice(0, exponent + 1) + "." + coefficient.slice(exponent + 1)
        : coefficient + new Array(exponent - coefficient.length + 2).join("0");
  }

  var formatTypes = {
    "%": function(x, p) { return (x * 100).toFixed(p); },
    "b": function(x) { return Math.round(x).toString(2); },
    "c": function(x) { return x + ""; },
    "d": function(x) { return Math.round(x).toString(10); },
    "e": function(x, p) { return x.toExponential(p); },
    "f": function(x, p) { return x.toFixed(p); },
    "g": function(x, p) { return x.toPrecision(p); },
    "o": function(x) { return Math.round(x).toString(8); },
    "p": function(x, p) { return formatRounded(x * 100, p); },
    "r": formatRounded,
    "s": formatPrefixAuto,
    "X": function(x) { return Math.round(x).toString(16).toUpperCase(); },
    "x": function(x) { return Math.round(x).toString(16); }
  };

  function identity(x) {
    return x;
  }

  var map = Array.prototype.map,
      prefixes = ["y","z","a","f","p","n","µ","m","","k","M","G","T","P","E","Z","Y"];

  function formatLocale(locale) {
    var group = locale.grouping === undefined || locale.thousands === undefined ? identity : formatGroup(map.call(locale.grouping, Number), locale.thousands + ""),
        currencyPrefix = locale.currency === undefined ? "" : locale.currency[0] + "",
        currencySuffix = locale.currency === undefined ? "" : locale.currency[1] + "",
        decimal = locale.decimal === undefined ? "." : locale.decimal + "",
        numerals = locale.numerals === undefined ? identity : formatNumerals(map.call(locale.numerals, String)),
        percent = locale.percent === undefined ? "%" : locale.percent + "",
        minus = locale.minus === undefined ? "-" : locale.minus + "",
        nan = locale.nan === undefined ? "NaN" : locale.nan + "";

    function newFormat(specifier) {
      specifier = formatSpecifier(specifier);

      var fill = specifier.fill,
          align = specifier.align,
          sign = specifier.sign,
          symbol = specifier.symbol,
          zero = specifier.zero,
          width = specifier.width,
          comma = specifier.comma,
          precision = specifier.precision,
          trim = specifier.trim,
          type = specifier.type;

      // The "n" type is an alias for ",g".
      if (type === "n") comma = true, type = "g";

      // The "" type, and any invalid type, is an alias for ".12~g".
      else if (!formatTypes[type]) precision === undefined && (precision = 12), trim = true, type = "g";

      // If zero fill is specified, padding goes after sign and before digits.
      if (zero || (fill === "0" && align === "=")) zero = true, fill = "0", align = "=";

      // Compute the prefix and suffix.
      // For SI-prefix, the suffix is lazily computed.
      var prefix = symbol === "$" ? currencyPrefix : symbol === "#" && /[boxX]/.test(type) ? "0" + type.toLowerCase() : "",
          suffix = symbol === "$" ? currencySuffix : /[%p]/.test(type) ? percent : "";

      // What format function should we use?
      // Is this an integer type?
      // Can this type generate exponential notation?
      var formatType = formatTypes[type],
          maybeSuffix = /[defgprs%]/.test(type);

      // Set the default precision if not specified,
      // or clamp the specified precision to the supported range.
      // For significant precision, it must be in [1, 21].
      // For fixed precision, it must be in [0, 20].
      precision = precision === undefined ? 6
          : /[gprs]/.test(type) ? Math.max(1, Math.min(21, precision))
          : Math.max(0, Math.min(20, precision));

      function format(value) {
        var valuePrefix = prefix,
            valueSuffix = suffix,
            i, n, c;

        if (type === "c") {
          valueSuffix = formatType(value) + valueSuffix;
          value = "";
        } else {
          value = +value;

          // Determine the sign. -0 is not less than 0, but 1 / -0 is!
          var valueNegative = value < 0 || 1 / value < 0;

          // Perform the initial formatting.
          value = isNaN(value) ? nan : formatType(Math.abs(value), precision);

          // Trim insignificant zeros.
          if (trim) value = formatTrim(value);

          // If a negative value rounds to zero after formatting, and no explicit positive sign is requested, hide the sign.
          if (valueNegative && +value === 0 && sign !== "+") valueNegative = false;

          // Compute the prefix and suffix.
          valuePrefix = (valueNegative ? (sign === "(" ? sign : minus) : sign === "-" || sign === "(" ? "" : sign) + valuePrefix;
          valueSuffix = (type === "s" ? prefixes[8 + prefixExponent / 3] : "") + valueSuffix + (valueNegative && sign === "(" ? ")" : "");

          // Break the formatted value into the integer “value” part that can be
          // grouped, and fractional or exponential “suffix” part that is not.
          if (maybeSuffix) {
            i = -1, n = value.length;
            while (++i < n) {
              if (c = value.charCodeAt(i), 48 > c || c > 57) {
                valueSuffix = (c === 46 ? decimal + value.slice(i + 1) : value.slice(i)) + valueSuffix;
                value = value.slice(0, i);
                break;
              }
            }
          }
        }

        // If the fill character is not "0", grouping is applied before padding.
        if (comma && !zero) value = group(value, Infinity);

        // Compute the padding.
        var length = valuePrefix.length + value.length + valueSuffix.length,
            padding = length < width ? new Array(width - length + 1).join(fill) : "";

        // If the fill character is "0", grouping is applied after padding.
        if (comma && zero) value = group(padding + value, padding.length ? width - valueSuffix.length : Infinity), padding = "";

        // Reconstruct the final output based on the desired alignment.
        switch (align) {
          case "<": value = valuePrefix + value + valueSuffix + padding; break;
          case "=": value = valuePrefix + padding + value + valueSuffix; break;
          case "^": value = padding.slice(0, length = padding.length >> 1) + valuePrefix + value + valueSuffix + padding.slice(length); break;
          default: value = padding + valuePrefix + value + valueSuffix; break;
        }

        return numerals(value);
      }

      format.toString = function() {
        return specifier + "";
      };

      return format;
    }

    function formatPrefix(specifier, value) {
      var f = newFormat((specifier = formatSpecifier(specifier), specifier.type = "f", specifier)),
          e = Math.max(-8, Math.min(8, Math.floor(exponent(value) / 3))) * 3,
          k = Math.pow(10, -e),
          prefix = prefixes[8 + e / 3];
      return function(value) {
        return f(k * value) + prefix;
      };
    }

    return {
      format: newFormat,
      formatPrefix: formatPrefix
    };
  }

  var locale;
  var format;
  var formatPrefix;

  defaultLocale({
    decimal: ".",
    thousands: ",",
    grouping: [3],
    currency: ["$", ""],
    minus: "-"
  });

  function defaultLocale(definition) {
    locale = formatLocale(definition);
    format = locale.format;
    formatPrefix = locale.formatPrefix;
    return locale;
  }

  function format$1(value, formatString) {
    // TODO:  Check what to do with legend's format call with parameters (legends.html.j2 e.g.)
    const formatFunc = formatString ? format(formatString) : formatValue;

    if (Array.isArray(value)) {
      const [first, second] = value;
      if (first === -Infinity) {
        return `< ${formatFunc(second)}`;
      }
      if (second === Infinity) {
        return `> ${formatFunc(first)}`;
      }
      return `${formatFunc(first)} - ${formatFunc(second)}`;
    }
    return formatFunc(value);
  }

  function formatValue(value) {
    if (typeof value === 'number') {
      return formatNumber(value);
    }
    return value;
  }

  function formatNumber(value) {
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

  function resetPopupClick(interactivity) {
    interactivity.off('featureClick');
  }

  function resetPopupHover(interactivity) {
    interactivity.off('featureHover');
  }

  function setPopupsClick(map, clickPopup, hoverPopup, interactivity, attrs) {
    interactivity.on('featureClick', (event) => {
      updatePopup(map, clickPopup, event, attrs);
      hoverPopup.remove();
    });
  }

  function setPopupsHover(map, hoverPopup, interactivity, attrs) {
    interactivity.on('featureHover', (event) => {
      updatePopup(map, hoverPopup, event, attrs);
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
            value = format$1(value, item.format);

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

    const clickPopup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: false
    });

    const hoverPopup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    const { clickAttrs, hoverAttrs } = _setInteractivityAttrs(interactiveLayers);

    resetPopupClick(map);
    resetPopupHover(map);

    if (clickAttrs.length > 0) {
      setPopupsClick(map, clickPopup, hoverPopup, interactivity, clickAttrs);
    }

    if (hoverAttrs.length > 0) {
      setPopupsHover(map, hoverPopup, interactivity, hoverAttrs);
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
      widget.element.innerText = typeof value === 'number' ? format$1(value, widget.options.format) : value;
    }
  }

  function renderBridge(bridge, widget, mapLayer) {
    widget.element = widget.element || document.querySelector(`#${widget.id}`);

    switch (widget.type) {
      case 'histogram':
        const type = _getWidgetType(mapLayer, widget.value, widget.prop);
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

    widgets
      .filter((widget) => widget.has_bridge)
      .forEach((widget) => renderBridge(bridge, widget, mapLayer));

    bridge.build();
  }

  function _getWidgetType(layer, property, value) {
    return layer.metadata && layer.metadata.properties[value] ?
      layer.metadata.properties[value].type
      : _getWidgetPropertyType(layer, property);
  }

  function _getWidgetPropertyType(layer, property) {
    return layer.metadata && layer.metadata.properties[property] ?
      layer.metadata.properties[property].type
      : null;
  }

  function createLegends(layer, legends, layerIndex, mapIndex=0) {
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
      const formatString = legend.format;
      const formatFunc = formatString
        ? (value) => format$1(value, formatString)
        : format$1;
      const options = { format: formatFunc, config, dynamic };

      if (legend.type.startsWith('size-continuous')) {
        config.samples = 4;
      }

      AsBridge.VL.Legends.rampLegend(element, layer, prop, options);
    }
  }

  function SourceFactory() {
    const sourceTypes = { GeoJSON, Query, MVT };

    this.createSource = (layer) => {
      return sourceTypes[layer.type](layer);
    };
  }

  function GeoJSON(layer) {
    const options = JSON.parse(JSON.stringify(layer.options));
    const data = _decodeJSONData(layer.data, layer.encode_data);

    return new carto.source.GeoJSON(data, options);
  }

  function Query(layer) {
    const auth = {
      username: layer.credentials.username,
      apiKey: layer.credentials.api_key || 'default_public'
    };

    const config = {
      serverURL: layer.credentials.base_url || `https://${layer.credentials.username}.carto.com/`
    };

    return new carto.source.SQL(layer.data, auth, config);
  }

  function MVT(layer) {
    return new carto.source.MVT(layer.data.file, JSON.parse(layer.data.metadata));
  }

  function _decodeJSONData(data, encodeData) {
    try {
      if (encodeData) {
        const decodedJSON = pako.inflate(atob(data), { to: 'string' });
        return JSON.parse(decodedJSON);
      } else {
        return JSON.parse(data);
      }
    } catch(error) {
      throw new Error(`
      Error: "${error}". CARTOframes is not able to parse your local data because it is too large.
      Please, disable the data compresion with encode_data=False in your Layer class.
    `);
    }
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

    mapLayer.addTo(map);

    setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends);
    setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource);

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
    if (hasLegends && layer.legends) {
      createLegends(mapLayer, layer.legends, mapLayerIndex, mapIndex);
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
    const isStatic = settings.is_static;
    const layers = settings.layers;
    const mapLayers = getMapLayers(
      layers,
      numLayers,
      hasLegends,
      map,
      mapIndex
    );

    if (settings.layer_selector) {
      addLayersSelector(layers.reverse(), mapLayers.reverse(), mapIndex);
    }

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

  function addLayersSelector(layers, mapLayers, mapIndex) {
    const layerSelectorId = mapIndex !== undefined ? `#layer-selector-${mapIndex}` : '#layer-selector';
    const layerSelector$ = document.querySelector(layerSelectorId);
    const layersInfo = mapLayers.map((layer, index) => {
      return {
        title: layers[index].title || `Layer ${index}`,
        id: layer.id,
        checked: true
      };
    });

    const layerSelector = new AsBridge.VL.Layers(layerSelector$, carto, layersInfo, mapLayers);
    
    layerSelector.build();
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
