export default function SourceFactory() {
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