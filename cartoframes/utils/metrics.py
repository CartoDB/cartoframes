import os
import uuid
import requests
import functools

from urllib.parse import urlparse

from .logger import log
from .utils import (default_config_path, read_from_config, save_in_config, is_uuid, get_local_time, silent_fail,
                    get_runtime_env, get_credentials, get_parameter_from_decorator)
from .. import __version__

EVENT_VERSION = '1'
EVENT_SOURCE = 'cartoframes'

UUID_KEY = 'uuid'
ENABLED_KEY = 'enabled'
METRICS_FILENAME = 'metrics.json'
CLOUD_API = 'cloud'
CUSTOM_API = 'custom'

PROD_DOMAIN_TLD = 'carto.com'
STAG_DOMAIN_TLD = 'carto-staging.com'
PROD_METRICS_SERVER = 'https://bmetrics.cartodb.net'
STAG_METRICS_SERVER = 'https://bmetrics-staging.cartodb.net'

_metrics_config = None


def setup_metrics(enabled):
    '''Update the metrics configuration.

    Args:
        enabled (bool): flag to enable/disable metrics.

    '''
    global _metrics_config

    _metrics_config[ENABLED_KEY] = enabled

    save_in_config(_metrics_config, filename=METRICS_FILENAME)


@silent_fail
def init_metrics_config():
    global _metrics_config

    filepath = default_config_path(METRICS_FILENAME)

    if _metrics_config is None:
        if os.path.exists(filepath):
            _metrics_config = read_from_config(filepath=filepath)

        if not check_valid_metrics_uuid(_metrics_config):
            _metrics_config = create_metrics_config()
            save_in_config(_metrics_config, filename=METRICS_FILENAME)


def create_metrics_config():
    return {
        UUID_KEY: str(uuid.uuid4()),
        ENABLED_KEY: True
    }


def get_metrics_uuid():
    if _metrics_config is not None:
        return _metrics_config.get(UUID_KEY)


def get_metrics_enabled():
    if _metrics_config is not None:
        return _metrics_config.get(ENABLED_KEY)


def check_valid_metrics_uuid(metrics_config):
    return metrics_config is not None and is_uuid(metrics_config.get(UUID_KEY))


def build_metrics_data(event_name, extra_metrics_data, server_domain_tld):
    metrics_data = {
        'event_version': EVENT_VERSION,
        'event_time': get_local_time(),
        'event_source': EVENT_SOURCE,
        'event_name': event_name,
        'source_version': __version__,
        'installation_id': get_metrics_uuid(),
        'runtime_env': get_runtime_env(),
        'api_used': get_api_used(server_domain_tld)
    }

    if isinstance(extra_metrics_data, dict):
        return {**metrics_data, **extra_metrics_data}

    return metrics_data


@silent_fail
def post_metrics(event_name, extra_metrics_data, server_domain_tld):
    metrics_server = STAG_METRICS_SERVER if server_domain_tld == STAG_DOMAIN_TLD else PROD_METRICS_SERVER
    json_data = build_metrics_data(event_name, extra_metrics_data, server_domain_tld)
    result = requests.post(metrics_server, json=json_data, timeout=2)
    log.debug('Metrics sent! {0} {1}'.format(result.status_code, json_data))


def send_metrics(event_name):
    def decorator_func(func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            result = func(*args, **kwargs)

            if get_metrics_enabled():
                extra_metrics_data, server_domain_tld = build_extra_metrics_data(func, *args, **kwargs)
                post_metrics(event_name, extra_metrics_data, server_domain_tld)

            return result
        return wrapper_func
    return decorator_func


def build_extra_metrics_data(decorated_function, *args, **kwargs):
    extra_metrics = {}
    server_domain_tld = PROD_DOMAIN_TLD

    try:
        credentials = get_parameter_from_decorator('credentials', decorated_function, *args, **kwargs)
        credentials = get_credentials(credentials)
        server_domain_tld = get_server_domain_tld(credentials.base_url)

        if credentials and credentials.user_id:
            extra_metrics['user_id'] = credentials.user_id

        return extra_metrics, server_domain_tld

    except Exception:
        return extra_metrics, server_domain_tld


def get_server_domain_tld(server_url):
    hostname = urlparse(server_url).hostname
    return '.'.join(hostname.split('.')[-2:])


def get_api_used(server_domain_tld):
    return CLOUD_API if server_domain_tld in [PROD_DOMAIN_TLD, STAG_DOMAIN_TLD] else CUSTOM_API


# Run this once
init_metrics_config()
