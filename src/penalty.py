class Penalty:
    def __init__(self, player_id, season, competition, club, date, against, minute, score_at_this_time, goalkeeper):
        self.player_id = player_id
        self.season = season
        self.competition = competition
        self.club = club
        self.date = date
        self.against = against
        self.minute = minute
        self.score_at_this_time = score_at_this_time
        self.goalleeper = goalkeeper