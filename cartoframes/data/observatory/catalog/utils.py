from .subscriptions import trigger_subscription
from .subscription_info import fetch_subscription_info
from ....utils.utils import is_ipython_notebook, check_package

if is_ipython_notebook():
    from IPython.display import display


def display_existing_subscription_message(entity_id, entity_type):
    if is_ipython_notebook():
        _display_existing_subscription_message_notebook(entity_id, entity_type)
    else:
        _display_existing_subscription_message_cli(entity_id, entity_type)


def display_subscription_form(entity_id, entity_type, credentials):
    info = fetch_subscription_info(entity_id, entity_type, credentials)
    instant_licensing = credentials.get_do_credentials().instant_licensing

    if is_ipython_notebook():
        _display_subscription_form_notebook(entity_id, entity_type, info, instant_licensing, credentials)
    else:
        _display_subscription_form_cli(entity_id, entity_type, info, instant_licensing, credentials)


def _display_existing_subscription_message_notebook(entity_id, entity_type):
    check_package('ipywidgets')

    from ipywidgets.widgets import HTML

    message = '''
        <h3>Subscription already purchased</h3>
        The {0} <b>{1}</b> has already been purchased.
        '''.format(entity_type, entity_id)
    display(HTML(message))


def _display_existing_subscription_message_cli(entity_id, entity_type):
    message = ('Subscription already purchased:\n' +
               'The {0} "{1}" has already been purchased.'.format(entity_type, entity_id))
    print(message)


def _display_subscription_form_notebook(entity_id, entity_type, info, instant_licensing, credentials):
    delivery_days = info.get('estimated_delivery_days')
    if instant_licensing and delivery_days == 0:
        delivery_message = '''
        This {type} is available for Instant Subscription for your organization,
        so it will automatically process the order and you will get immediate access to the {type}.
        '''.format(type=entity_type)
    else:
        delivery_message = '''
        This {type} will be available in your account in about {days} days.
        We will contact you shortly to complete the subscription details.
        '''.format(type=entity_type, days=delivery_days)

    price = info.get('subscription_list_price')
    if price is None:
        message = '''
        <h3>Data request</h3>
        You are about to request the {type} <b>{id}</b>.
        <br>Do you want to proceed?
        '''.format(
            id=entity_id,
            type=entity_type)

        responses = {
            'ok': '''
            <b>Thanks!</b><br>The {type} <b>{id}</b> has been requested.
            We will contact you shortly to complete the subscription details.
            '''.format(id=entity_id, type=entity_type),
            'cancel': '''
            The {type} <b>{id}</b> has not been requested.
            '''.format(id=entity_id, type=entity_type),
            'error': '''
            Request error. Please contact to support@carto.com.
            '''}
    else:
        message = '''
        <h3>Subscription contract</h3>
        You are about to subscribe to <b>{id}</b>.
        The cost of this {type} is <b>${price}</b>.
        If you want to proceed, a Request will be sent to CARTO who will
        order the data and load it into your account.
        {delivery_message}
        In order to proceed we need you to agree to the License of the {type}
        available at <b><a href="{link}" target="_blank">this link</a></b>.
        <br>Do you want to proceed?
        '''.format(
            id=entity_id,
            type=entity_type,
            price=price,
            delivery_message=delivery_message,
            link=info.get('tos_link'))

        responses = {
            'ok': '''
            <b>Congrats!</b><br>The {type} <b>{id}</b> has been requested and it
            will be available in your account soon.
            '''.format(id=entity_id, type=entity_type),
            'cancel': '''
            The {type} <b>{id}</b> has not been purchased.
            '''.format(id=entity_id, type=entity_type),
            'error': '''
            Subscription error. Please contact to support@carto.com.
            '''}

    text, buttons = _create_notebook_form(entity_id, entity_type, message, responses, credentials)

    display(text, buttons)


def _create_notebook_form(entity_id, entity_type, message, responses, credentials):
    check_package('ipywidgets')

    from ipywidgets.widgets import HTML, Layout, Button, GridspecLayout

    text = HTML(message)

    button_yes = Button(
        description='Yes', button_style='info', layout=Layout(height='32px', width='176px'))
    button_no = Button(
        description='No', button_style='', layout=Layout(height='32px', width='176px'))

    buttons = GridspecLayout(1, 5)
    buttons[0, 0] = button_yes
    buttons[0, 1] = button_no

    def disable_buttons():
        button_yes.disabled = True
        button_no.disabled = True

    def on_button_yes_clicked(b):
        disable_buttons()
        response = trigger_subscription(entity_id, entity_type, credentials)
        if response:
            display(HTML(responses.get('ok')))
        else:
            display(HTML(responses.get('error')))

    def on_button_no_clicked(b):
        disable_buttons()
        display(HTML(responses.get('cancel')))

    button_yes.on_click(on_button_yes_clicked)
    button_no.on_click(on_button_no_clicked)

    return (text, buttons)


def _display_subscription_form_cli(entity_id, entity_type, info, instant_licensing, credentials):
    delivery_days = info.get('estimated_delivery_days')
    if instant_licensing and delivery_days == 0:
        delivery_message = (
            'This {type} is available for Instant Subscription for your organization, '
            'so it will automatically process the order and you will get immediate access to the {type}.'
        ).format(type=entity_type)
    else:
        delivery_message = (
            'This {type} will be available in your account in about {days} days. '
            'We will contact you shortly to complete the subscription details.'
        ).format(type=entity_type, days=delivery_days)

    price = info.get('subscription_list_price')
    if price is None:
        message = (
            'Data request:\n'
            'You are about to request the {type} "{id}".\n'
            'Do you want to proceed?').format(
                id=entity_id,
                type=entity_type)

        responses = {
            'ok': ('Thanks! The {type} "{id}" has been requested. We will contact you shortly to '
                   'complete the subscription details.').format(id=entity_id, type=entity_type),
            'cancel': 'The {type} "{id}" has not been requested'.format(id=entity_id, type=entity_type),
            'error': 'Request error. Please contact to support@carto.com.'}
    else:
        message = (
            'Subscription contract:\n'
            'You are about to subscribe to "{id}". '
            'The cost of this {type} is ${price}. '
            'If you want to proceed, a Request will be sent to CARTO who will '
            'order the data and load it into your account. '
            '{delivery_message} '
            'In order to proceed we need you to agree to the License of the {type} '
            'available at this link: {link}.\n'
            'Do you want to proceed?').format(
                id=entity_id,
                type=entity_type,
                price=price,
                delivery_message=delivery_message,
                link=info.get('tos_link'))

        responses = {
            'ok': ('Congrats! The {type} "{id}" has been requested and '
                   'it will be available in your account soon.').format(id=entity_id, type=entity_type),
            'cancel': 'The {type} "{id}" has not been purchased'.format(id=entity_id, type=entity_type),
            'error': 'Subscription error. Please contact to support@carto.com.'}

    response = _create_cli_form(entity_id, entity_type, message, responses, credentials)

    print(response)


def _create_cli_form(entity_id, entity_type, message, responses, credentials):
    answer_yes = input('{} (y/N): '.format(message)).lower() == 'y'

    if answer_yes:
        response = trigger_subscription(entity_id, entity_type, credentials)
        if response:
            return responses.get('ok')
        else:
            return responses.get('error')
    else:
        return responses.get('cancel')
