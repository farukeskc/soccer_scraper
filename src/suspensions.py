class Suspension:
    def __init__(self, player_id, season, suspension, competition, start_date, end_date, days, games_missed):
        self.player_id = player_id
        self.season = season
        self.suspension = suspension
        self.competition = competition
        self.start_date = start_date
        self.end_date = end_date
        self.days = days
        self.games_missed = games_missed