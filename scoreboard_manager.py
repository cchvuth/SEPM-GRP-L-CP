import json


class ScoreboardManager:
    def __init__(self):
        self.score = {}

    def __inc_score(self, username, score):
        try:
            self.score[username] += score
        except:
            self.score[username] = 0
            self.score[username] += score

    def reset_tournament(self):
        self.score = {}
    
    def add_score(self, winner_username, loser_username):
        self.__inc_score(winner_username, 1)
        self.__inc_score(loser_username, 0)
        return self.to_json()

    def add_draw(self, first_username, second_username):
        self.__inc_score(first_username, 1)
        self.__inc_score(second_username, 1)
        return self.to_json()

    def to_json(self):
        return json.dumps(self.score)


scoreboard_manager = ScoreboardManager()
