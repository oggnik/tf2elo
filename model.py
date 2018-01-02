
class Match:
    def __init__(self, team1, team2, map, date):
        self.team1 = team1
        self.team2 = team2
        self.date = date
        self.completed = False
        self.orig_completed = False
        self.team1_score = 0
        self.team2_score = 0
        self.winner = ''
        self.map = map
        self.t1_prob = 0.5
        self.t2_prob = 0.5

    def set_scores(self, t1_score, t2_score):
        self.completed = True
        self.team1_score = t1_score
        self.team2_score = t2_score
        self.winner = self.team1 if t1_score > t2_score else self.team2
        self.t1_prob = 1.0 if t1_score > t2_score else 0.0
        self.t2_prob = 1.0 - self.t1_prob

class Team:
    def __init__(self, name):
        self.name = name
        self.matches_for = 0
        self.matches_against = 0
        self.elo = 1500
        self.num_playoffs = 0
