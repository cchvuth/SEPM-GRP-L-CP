class PlayerManager:
    def __init__(self, username, conn, conn_id):
        self.username = username
        self.conn = conn
        self.conn_id = conn_id
        self.game_id = None
        self.player_side = None
        self.prev_opponents = []
    
    def join_game(self, game_id, player_side):
        self.game_id = game_id
        self.player_side = player_side
    
    def leave_game(self):
        self.game_id = None

    def add_prev_opponent(self, conn_id):
        self.prev_opponents.append(conn_id)

    def is_prev_opponent(self, conn_id):
        return conn_id in self.prev_opponents or conn_id == self.conn_id

    def prev_opponent_counts(self):
        return len(self.prev_opponents)
