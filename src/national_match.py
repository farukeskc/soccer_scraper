class NationalMatch:
    def __init__(self, player_id, competition, matchday, club, venue, date, home_team, away_team, result, position,
                 goal, assist, own_goal, yellow, second_yellow, red, substitutions_on, substitutions_off,
                 minutes_played):
        self.player_id = player_id
        self.competition = competition
        self.matchday = matchday
        self.club = club
        self.venue = venue
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.result = result
        self.position = position
        self.goal = goal
        self.assist = assist
        self.own_goal = own_goal
        self.yellow = yellow
        self.second_yellow = second_yellow
        self.red = red
        self.substitutions_on = substitutions_on
        self.substitutions_off = substitutions_off
        self.minutes_played = minutes_played
