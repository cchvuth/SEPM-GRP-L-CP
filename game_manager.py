import uuid


class Game:
    def __init__(self, state):
        self.state = state
        self.conn_ids = [None] * 2

    def add_conn_id(self, player_side, conn_id):
        self.conn_ids[player_side] = conn_id


class GameManager:
    def __init__(self):
        self.active_games = {}
        self.player_in_game_counts = 0

    def get_game(self, id):
        return self.active_games[id]

    def del_game(self, id):
        del self.active_games[id]
        return True
    
    def increment_player_in_game(self, by = 1):
        self.player_in_game_counts += by

    def decrement_player_in_game(self, by = 1):
        self.player_in_game_counts -= by
        print('Decrement player in game', self.player_in_game_counts)

    def register_game(self):
        game_id = str(uuid.uuid1())
        self.active_games[game_id] = Game('game_created')
        print('Game', game_id, 'created')
        return game_id

    def setup_game(self, first_player_conn_id, second_player_conn_id):
        from connection_manager import connection_manager
        from queue_manager import queue_manager

        first_player = connection_manager.get_player(first_player_conn_id)
        first_player.player_side = (first_player.player_side or 1 + 1) % 2

        second_player = connection_manager.get_player(second_player_conn_id)
        second_player.player_side = (first_player.player_side + 1) % 2

        if queue_manager.mode == 'tournament':
            first_player.add_prev_opponent(second_player_conn_id)
            second_player.add_prev_opponent(first_player_conn_id)

        game_id = self.register_game()
        game = game_manager.get_game(game_id)

        for player in [first_player, second_player]:
            player.join_game(game_id, player.player_side)
            game.add_conn_id(player.player_side, player.conn_id)

        self.increment_player_in_game(2)

        game.state = 'game_ready'
        print('Game ready', game_id)
        return game_id


game_manager = GameManager()
