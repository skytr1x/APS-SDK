class HostError(Exception):
    def __init__(self, key, **params):
        super().__init__(key)
        self.key = key
        self.params = params
