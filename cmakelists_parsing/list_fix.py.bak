class List(list):
    """
    Same as pypeg2.List except that the constructor has been modified
    to work with Python 2.x.

    See http://goo.gl/VKPY3.
    """

    def __init__(self, *args, **kwargs):
        """Construct a List, and construct its attributes from keyword
        arguments.
        """
        if len(args) == 1:
            if isinstance(args[0], str):
                self.append(args[0])
            else:
                super(List, self).__init__(args[0])
        else:
            super(List, self).__init__(args)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return ''.join((type(self).__name__, "(", super(List, self).__repr__(),
            ")"))

    def __eq__(self, other):
        return super(List, self).__eq__(list(other))
