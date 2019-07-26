Credentials Management
======================

Typical usage
^^^^^^^^^^^^^

The most common way to input credentials into cartoframes is through the `set_default_credentials` method, as below. Replace `{your_user_name}` with your CARTO username and `{your_api_key}` with your API key, which you can find at ``https://{your_user_name}.carto.com/your_apps``.

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        username='{your_user_name}',
        api_key='{your_api_key}'
    )

You can also set your credentials using the `base_url` parameter:

.. code:: python

    from cartoframes.auth import set_default_credentials

    set_default_credentials(
        base_url='https://{your_user_name}.carto.com',
        api_key='{your_api_key}'
    )


The Credentials class
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: cartoframes.auth.credentials
    :noindex:
    :members:
