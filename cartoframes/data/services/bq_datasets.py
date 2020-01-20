

class BQDataset:

    def __init__(self, name_id):
        self.name = name_id

    def download_stream(self):
        pass


class BQUserDataset:

    @staticmethod
    def name(name_id):
        return BQDataset(name_id)
