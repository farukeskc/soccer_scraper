import datetime


class Transfer:
    def __init__(self, player_id, season, date, left, joined, market_value, fee):
        self.player_id = player_id
        self.season = season
        self.date = date
        self.left = left
        self.joined = joined
        self.market_value = market_value
        self.fee = fee

