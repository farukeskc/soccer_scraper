class Stats:
    def __init__(self, player_id, season, competition, club, squad, appearances,
                 point_per_game, goals, assists, own_goals, substitutions_on,
                 substitutions_off, yellow, second_yellow, red, penalty_goals, minutes_per_goal, minutes
                 ):
        self.player_id = player_id
        self.season = season
        self.competition = competition
        self.club = club
        self.squad = squad
        self.appearancess = appearances
        self.point_per_game = point_per_game
        self.goals = goals
        self.assists = assists
        self.own_goals = own_goals
        self.substitutions_on = substitutions_on
        self.substitutions_off = substitutions_off
        self.yellow = yellow
        self.second_yellow = second_yellow
        self.red = red
        self.penalty_goals = penalty_goals
        self.minutes_per_goal = minutes_per_goal
        self.minutes = minutes
