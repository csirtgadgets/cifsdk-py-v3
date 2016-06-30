from cifsdk.format import COLUMNS, MAX_FIELD_SIZE


class Plugin(object):

    def __init__(self, data, cols=COLUMNS, max_field_size=MAX_FIELD_SIZE):
        self.cols = cols
        self.max_field_size = max_field_size
        self.data = data

    def __repr__(self):
        raise NotImplementedError