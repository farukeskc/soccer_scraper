class PlayerNameUrl:
    def __init__(self, name, url, market_value):
        self.name = name
        self.url = url
        self.market_value = market_value

    def __eq__(self, other):
        if isinstance(other, PlayerNameUrl):
            return self.name == other.name and self.url == other.url and self.market_value == other.market_value
        return False
