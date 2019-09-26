import os


def auth(credentials):

    if not credentials:
        raise ValueError('You should set credentials')

    return os.environ['GOOGLE_APPLICATION_CREDENTIALS']
