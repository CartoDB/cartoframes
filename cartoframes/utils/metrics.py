import os
import uuid

from .utils import default_config_path, read_from_config, save_in_config, is_uuid

UUID_KEY = 'uuid'
ENABLED_KEY = 'enabled'
METRICS_FILENAME = 'metrics.json'

_metrics_config = None


def setup_metrics(enabled):
    """Update the metrics configuration.

    Args:
        enabled (bool): flag to enable/disable metrics.

    """
    global _metrics_config

    _metrics_config[ENABLED_KEY] = enabled

    save_in_config(_metrics_config, filename=METRICS_FILENAME)


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


# Run this once
init_metrics_config()
