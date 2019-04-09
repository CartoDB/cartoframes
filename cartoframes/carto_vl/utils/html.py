class HTMLMap(object):
    def __init__(self, content):
        self.content = content

    def _repr_html_(self):
        return self.content
