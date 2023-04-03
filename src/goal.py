class Goal:
    def __init__(self, player_id, competition, matchday, date, venue, club, against, result, position, minute, at_score, type_of_goal, assist):
        self.player_id = player_id
        self.competition = competition
        self.matchday = matchday
        self.date = date
        self.venue = venue
        self.club = club
        self.against = against
        self.result = result
        self.position = position
        self.minute = minute
        self.at_score = at_score
        self.type_of_goal = type_of_goal
        self.assist = assist