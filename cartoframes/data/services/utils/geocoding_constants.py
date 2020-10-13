__all__ = [
    'HASH_COLUMN',
    'DEFAULT_STATUS',
    'QUOTA_SERVICE',
    'STATUS_FIELDS',
    'STATUS_FIELDS_KEYS',
    'GEOCODE_COLUMN_KEY',
    'GEOCODE_VALUE_KEY',
    'VALID_GEOCODE_KEYS'
]

HASH_COLUMN = 'carto_geocode_hash'

DEFAULT_STATUS = {'gc_status_rel': 'relevance'}

QUOTA_SERVICE = 'hires_geocoder'

STATUS_FIELDS = {
    'relevance': ('numeric', "(_g.metadata->>'relevance')::numeric"),
    'precision': ('text', "_g.metadata->>'precision'"),
    'match_types': ('text', "cdb_dataservices_client.cdb_jsonb_array_casttext(_g.metadata->>'match_types')"),
    '*': ('jsonb', "_g.metadata")
}

STATUS_FIELDS_KEYS = sorted(STATUS_FIELDS.keys())

GEOCODE_COLUMN_KEY = 'column'

GEOCODE_VALUE_KEY = 'value'

VALID_GEOCODE_KEYS = [GEOCODE_COLUMN_KEY, GEOCODE_VALUE_KEY]
