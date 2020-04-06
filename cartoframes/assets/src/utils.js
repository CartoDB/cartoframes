
export function format(value) {
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

export function formatValue(value) {
  if (typeof value === 'number') {
    return formatNumber(value);
  }
  return value;
}

export function formatNumber(value) {
  if (!Number.isInteger(value)) {
    return value.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 3
    });
  }
  return value.toLocaleString();
}

export function updateViewport(map) {
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

export function getBasecolorSettings(basecolor) {
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

export function getImageElement(mapIndex) {
  const id = mapIndex !== undefined ? `map-image-${mapIndex}` : 'map-image';
  return document.getElementById(id);
}

export function getContainerElement(mapIndex) {
  const id = mapIndex !== undefined ? `main-container-${mapIndex}` : 'main-container';
  return document.getElementById(id);
}

export function saveImage(mapIndex) {
  const img = getImageElement(mapIndex);
  const container = getContainerElement(mapIndex);

  html2canvas(container)
    .then((canvas) => setMapImage(canvas, img, container));
}

export function setMapImage(canvas, img, container) {
  const src = canvas.toDataURL();
  img.setAttribute('src', src);
  img.style.display = 'block';
  container.style.display = 'none';
}