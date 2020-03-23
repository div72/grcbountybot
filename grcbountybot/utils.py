class DotDict:
    def _unpack(self, iterable):
        for i, item in enumerate(iterable):
            if isinstance(item, dict):
                iterable[i] = DotDict(**item)
            elif isinstance(item, list):
                self._unpack(item)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = DotDict(**value)
            elif isinstance(value, list):
                self._unpack(value)
            setattr(self, key, value)
