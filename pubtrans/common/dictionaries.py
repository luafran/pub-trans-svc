class DictAsObject(dict):  # pylint: disable=too-few-public-methods
    def __init__(self, *args, **kwargs):
        super(DictAsObject, self).__init__(*args, **kwargs)
        self.__dict__ = self
