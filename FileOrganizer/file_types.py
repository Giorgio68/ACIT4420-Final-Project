"""
Contains all available file types that can be processed
"""


class Map(dict):
    """
    Allows accessing elements using dots
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor method
        """
        super().__init__(*args, **kwargs)

        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = type(self)(v)

                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = type(self)(v)

                else:
                    self[k] = v

    def __getattr__(self, attr, default=None):
        return self.get(attr, default)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if isinstance(value, dict):
            self.__dict__.update({key: type(self)(value)})

        else:
            self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]


types = Map(
    {
        "python": {"extension": ["py", "pyc"]},
        "text": {"extension": ["txt"]},
        "json": {"extension": ["json", "jsonl"]},
        "executables": {"extension": ["exe"]},
        "image": {"extension": ["png", "jpg", "svg", "tiff", "webp"]},
        "video": {"extension": ["mp4"]},
    }
)
