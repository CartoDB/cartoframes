export const BASEMAPS = {
  DarkMatter: carto.basemaps.darkmatter,
  Voyager: carto.basemaps.voyager,
  Positron: carto.basemaps.positron
};

export const attributionControl = new mapboxgl.AttributionControl({
  compact: false
});

export const FIT_BOUNDS_SETTINGS = { animate: false, padding: 50, maxZoom: 16 };