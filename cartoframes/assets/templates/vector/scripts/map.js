const responsive = document.querySelector('as-responsive-content');

function onReady() {
  const BASEMAPS = {
    DarkMatter: carto.basemaps.darkmatter,
    Voyager: carto.basemaps.voyager,
    Positron: carto.basemaps.positron
  };

  if ("{{mapboxtoken}}") {
    mapboxgl.accessToken = "{{mapboxtoken}}";
  }

  // Fetch CARTO basemap if it's there, else try to use other supplied style
  const map = new mapboxgl.Map({
    container: 'map',
    style: BASEMAPS['{{basemapstyle}}'] || "{{basemapstyle}}",
    zoom: 9,
    dragRotate: false
  });

  let credentials = {{credentials}};

  carto.setDefaultAuth({
    username: credentials['username'],
    apiKey: credentials['api_key'] || 'default_public'
  });

  carto.setDefaultConfig({
      serverURL: credentials['base_url'] || `https://${credentials['user']}.carto.com/`
  });

  var sources = {{sources}};

  map.fitBounds({{bounds}}, {animate: false});

  {% if camera != none %}
    map.flyTo({{ camera|clear_none|tojson }});
  {% endif %}

  sources.forEach((elem, idx) => {
    let temp_source = null;
    if (elem.is_local) {
      let local_json = JSON.parse(elem.source);
      temp_source = new carto.source.GeoJSON(local_json);
    } else {
      temp_source = new carto.source.SQL(elem.source);
    }
    const viz = new carto.Viz(elem['styling']);
    let temp = new carto.Layer(
        'layer' + idx,
        temp_source,
        viz
    );
    var last_source = idx === 0 ? 'watername_ocean' : 'layer' + (idx - 1);
    temp.addTo(map);

    // When layer loads, trigger legend event
    temp.on('loaded', () => {
        // Request data for legend from the layer viz
        if (viz.color.getLegendData) {
            const colorLegend = viz.color.getLegendData();
            let colorLegendList = '';

            // Create list elements for legend
            colorLegend.data.forEach((legend, index) => {
                const color = legend.value;
                const keyMin = legend.key[0].toFixed(2);
                const keyMax = legend.key[1].toFixed(2);
                let bucket = `${keyMin} - ${keyMax}`;
                if (keyMin === '-Infinity') {
                  bucket = `< ${keyMax}`;
                } else if (keyMax === 'Infinity') {
                  bucket = `> ${keyMin}`;
                }
                // Style for legend items
                colorLegendList +=
                        `<li style="color: rgb(${color.r}, ${color.g}, ${color.b}); font-size: 300%;" class="as-list__item"><span style="vertical-align: middle;" class="as-color--type-01 as-body as-font--medium">${bucket}</span></li>\n`;
            });

            const legend = `<section class="as-box">
                <h1 class="as-subheader">${elem.legend || 'Layer ' + idx}</h1>
                <div class="legend as-body">
                  <ul class="as-list">
          ${colorLegendList}
                  </ul>
                </div>
        </section>`;
            document.getElementById('legends').style.display = 'block';
            // Place list items in the content section of the title/legend box
            document.getElementById('legends').innerHTML += legend;
        }
    });

    if (elem.interactivity) {
      let interactivity = new carto.Interactivity(temp);
      let tempPopup = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
              });
      if (elem.interactivity.event == 'click') {
        setPopupsClick(tempPopup, interactivity, elem.interactivity.header);
      } else if (elem.interactivity.event == 'hover') {
        setPopupsHover(tempPopup, interactivity, elem.interactivity.header);
      }
    }
  });
  function setPopupsClick(tempPopup, intera, popupHeader) {
    intera.off('featureHover', (event) => {
        updatePopup(tempPopup, event, popupHeader)
    });
    intera.on('featureClick', (event) => {
        updatePopup(tempPopup, event, popupHeader, popupHeader)
    });
  }
  function setPopupsHover(tempPopup, intera, popupHeader) {
    intera.off('featureClick', (event) => {
        updatePopup(tempPopup, event, popupHeader)
    });
    intera.on('featureHover', (event) => {
        updatePopup(tempPopup, event, popupHeader)
    });
  }
  function updatePopup(layer_popup, event, popupHeader) {
    if (event.features.length > 0) {
      const vars = event.features[0].variables;
      let popupHTML = popupHeader ? `<h1>${popupHeader}</h1>` : ``;
      Object.keys(vars).forEach((varName) => {
          popupHTML += `
              <h3 class="h3">${varName}</h3>
              <p class="description open-sans">${vars[varName].value}</p>
          `;
      });
      layer_popup.setLngLat([event.coordinates.lng, event.coordinates.lat])
          .setHTML(`<div>${popupHTML}</div>`);
      if (!layer_popup.isOpen()) {
        layer_popup.addTo(map);
      }
    } else {
      layer_popup.remove();
    }
  }
}

responsive.addEventListener('ready', onReady);