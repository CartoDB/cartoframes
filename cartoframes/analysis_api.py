from IPython.display import display, clear_output

class NotebookOutput:
    @staticmethod
    def print(*args):
        # display(*args)
        print(*args)

    @staticmethod
    def clear():
        clear_output(wait=True)

from analysis import Analysis

def analysis_api(cc, url_base=None):
    url_base = url_base or 'https://{user}.carto.com/api/v4/analysis'.format(user=cc.auth_api_client.username)
    api_config = {
        'url_base': url_base,
        'user': cc.auth_api_client.username,
        'api_key': cc.auth_api_client.api_key
    }
    return Analysis(
        api_config,
        minimum_update_time=4,
        output=NotebookOutput
    )
