import json


class ScoreboardManager:
    def __init__(self):
        self.score = {}
    
    def reset_tournament(self):
        self.score = {}
    
    def add_score(self, winner_username, loser_username):
        try:
            self.score[winner_username] += 1
        except:
            self.score[winner_username] = 0
            self.score[winner_username] += 1
        
        try:
            self.score[loser_username] += 0
        except:
            self.score[loser_username] = 0
            self.score[loser_username] += 0
        
        return self.to_json()

    def to_json(self):
        return json.dumps(self.score)


scoreboard_manager = ScoreboardManager()
