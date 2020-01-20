import { formatValue } from '../utils';

export function resetPopupClick(interactivity) {
  interactivity.off('featureClick');
}

export function resetPopupHover(interactivity) {
  interactivity.off('featureHover');
}

export function setPopupsClick(map, clickPopup, hoverPopup, interactivity, attrs) {
  interactivity.on('featureClick', (event) => {
    updatePopup(map, clickPopup, event, attrs);
    hoverPopup.remove();
  });
}

export function setPopupsHover(map, hoverPopup, interactivity, attrs) {
  interactivity.on('featureHover', (event) => {
    updatePopup(map, hoverPopup, event, attrs);
  });
}

export function updatePopup(map, popup, event, attrs) {
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