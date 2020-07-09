export default function SourceFactory() {
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