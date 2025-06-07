class Strategy:
    registry = {}

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if name:
            Strategy.registry[name] = cls()

    def execute(self, df, owned_stocks, price, capital):
        raise NotImplementedError