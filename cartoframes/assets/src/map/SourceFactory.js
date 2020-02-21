export default function SourceFactory() {
  const sourceTypes = { GeoJSON, Query, MVT, BQMVT };

  this.createSource = (layer) => {
    return sourceTypes[layer.type](layer);
  };
}

function GeoJSON(layer) {
  const options = JSON.parse(JSON.stringify(layer.options));
  const data = _decodeJSONData(layer.data);

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

function BQMVT(layer) {
  const data = Object.assign(layer.data.data, {});
  const metadata = Object.assign(layer.data.metadata, {});
  console.log(data, metadata)
  return new carto.source.BQMVT(data, metadata, {
    viewportZoomToSourceZoom: (zoom) => {
      if (zoom >= 11) {
        return 12;
      }
      return null;
    }
  });
}

function _decodeJSONData(b64Data) {
  return JSON.parse(pako.inflate(atob(b64Data), { to: 'string' }));
}