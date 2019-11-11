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

function _decodeJSONData(b64Data) {
  // Decode base64 (convert ascii to binary)
  var strData = atob(b64Data);

  // Convert binary string to character-number array
  var charData = strData.split('').map((x) => { return x.charCodeAt(0); });

  // Turn number array into byte-array
  var binData = new Uint8Array(charData);

  // Pako magic
  var data = pako.inflate(binData);

  // Convert gunzipped byteArray back to ascii string:
  var strData = String.fromCharCode.apply(null, new Uint16Array(data));

  return JSON.parse(strData);
}