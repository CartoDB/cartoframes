export default function SourceFactory() {
  const sourceTypes = { GeoJSON, Query, MVT };

  this.createSource = (layer) => {
    return sourceTypes[layer.type](layer);
  };
}

function GeoJSON(layer) {
  return new carto.source.GeoJSON(_decodeJSONData(layer.data));
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

function _decodeJSONData(data) {
  return JSON.parse(Base64.decode(data.replace(/b\'/, '\'')));
}