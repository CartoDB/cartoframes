from .subscriptions import trigger_subscription
from .subscription_info import fetch_subscription_info

from ....core.logger import log


def is_ipython_notebook():
    """
    Detect whether we are in a Jupyter notebook.
    """
    try:
        cfg = get_ipython().config
        if 'IPKernelApp' in cfg:
            return True
        else:
            return False
    except NameError:
        return False


if is_ipython_notebook():
    from IPython.display import display
    from ipywidgets.widgets import HTML, Layout, Button, GridspecLayout


def display_existing_subscription_message(entity_id, entity_type):
    if is_ipython_notebook():
        _display_existing_subscription_message_notebook(entity_id, entity_type)
    else:
        _display_existing_subscription_message_cli(entity_id, entity_type)


def display_subscription_form(entity_id, entity_type, credentials):
    info = fetch_subscription_info(entity_id, entity_type, credentials)

    if is_ipython_notebook():
        _display_subscription_form_notebook(entity_id, entity_type, info, credentials)
    else:
        _display_subscription_form_cli()


def _display_existing_subscription_message_notebook(entity_id, entity_type):
    message = '''
        <h3>Subscription already purchased</h3>
        The {0} <b>{1}</b> has already been purchased.
        '''.format(entity_type, entity_id)
    text = HTML(message)
    display(text)


def _display_existing_subscription_message_cli(entity_id, entity_type):
    message = ('Subscription already purchased:\n' +
               '- The {0} "{1}" has already been purchased.'.format(entity_type, entity_id))
    print(message)


def _display_subscription_form_notebook(entity_id, entity_type, info, credentials):
    message = '''
    <h3>Subscription contract</h3>
    You are about to subscribe to <b>{id}</b>.
    The cost of this {type} is <b>${price}</b>.
    If you want to proceed, a Request will be sent to CARTO who will
    order the data and load it into your account.
    This {type} is available for Instant Order for your organization,
    so it will automatically process the order and you will get immediate access to the {type}.
    In order to proceed we need you to agree to the License of the {type}
    available at <b><a href="{link}" target="_blank">this link</a></b>.
    <br>Do you want to proceed?
    '''.format(
        id=entity_id,
        type=entity_type,
        price=info.get('subscription_list_price'),
        link=info.get('tos_link'))

    ok_response = '''
    <b>Congrats!</b><br>The {type} <b>{id}</b> has been requested and it will be available in your account soon.
    '''.format(id=entity_id, type=entity_type)

    cancel_message = '''
    The {type} <b>{id}</b> has not been purchased.
    '''.format(id=entity_id, type=entity_type)

    text, buttons = _create_notebook_form(
        entity_id, entity_type, message, ok_response, cancel_message, credentials)

    display(text, buttons)


def _create_notebook_form(entity_id, entity_type, message, ok_response, cancel_message, credentials):
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
            display(HTML(ok_response))
        else:
            display(HTML('Error'))

    def on_button_no_clicked(b):
        disable_buttons()
        display(HTML(cancel_message))

    button_yes.on_click(on_button_yes_clicked)
    button_no.on_click(on_button_no_clicked)

    return (text, buttons)


def _display_subscription_form_cli():
    log.info('This method is not yet implemented in CLI')
