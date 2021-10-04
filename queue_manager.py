from transfer_protocol import send_data
from game_manager import game_manager
from scoreboard_manager import scoreboard_manager
import time
import os


class QueueManager:
    def __init__(self):
        self.waiting_conn_ids = []
        self.tournament_started = False
        self.mode = ''

    def add_player(self, conn_id):
        self.waiting_conn_ids.append(conn_id)
        print('Player', conn_id, 'is waiting')

    def remove_player(self, conn_id):
        print('Removing', conn_id, 'from queue')
        try:
            self.waiting_conn_ids.remove(conn_id)
        except:
            pass
    
    def end_tournament(self):
        from connection_manager import connection_manager
        print('Ending tournament')

        for conn_id, player in connection_manager.conn_map.items():
            send_data(player.conn, 'tournament_ended')

        self.tournament_started = False

        time.sleep(.5)

        for conn_id, player in connection_manager.conn_map.items():
            send_data(player.conn, scoreboard_manager.to_json())
            connection_manager.close_conn(conn_id, False)

        os._exit(1)

    def find_match(self):
        from connection_manager import connection_manager

        conn_counts = connection_manager.conn_counts

        print('Finding match for', self.waiting_conn_ids)
        for player_conn_id in self.waiting_conn_ids:
            try:
                player = connection_manager.get_player(player_conn_id)
                print('Player', player.username, 'played', player.prev_opponent_counts())
            except:
                self.waiting_conn_ids.remove(player_conn_id)
                continue

            if player.prev_opponent_counts() == conn_counts - 1:
                print('Skipping')
                continue
            else:
                opponent_candidates = []
                for candidate in self.waiting_conn_ids:
                    if not player.is_prev_opponent(candidate):
                        opponent_candidates.append(candidate)

                print('Candidates:', opponent_candidates)

                if len(opponent_candidates) > 0:
                    opponent_conn_id = opponent_candidates[0]
                    print('Found match:', player_conn_id, 'vs', opponent_conn_id)
                    return player_conn_id, opponent_conn_id
        
        return None, None

    def start_game(self):
        from connection_manager import connection_manager

        first_player_conn_id, second_player_conn_id = self.find_match()

        if first_player_conn_id is None or second_player_conn_id is None:
            print('No more match available')
            everyone_played = True

            if game_manager.player_in_game_counts > 0:
                return False

            for conn_id, player in connection_manager.conn_map.items():
                print('Checking player', player.username, 'if player played with everyone')
                print(player.prev_opponent_counts(), connection_manager.conn_counts)

                if player.prev_opponent_counts() < connection_manager.conn_counts - 1:
                    everyone_played = False
                    print('But not all players played with each other yet')
                    break

            if not everyone_played:
                return False
            else:
                time.sleep(.5)
                self.end_tournament()
                return True

        game_id = game_manager.setup_game(first_player_conn_id, second_player_conn_id)

        for player_conn_id in [first_player_conn_id, second_player_conn_id]:
            self.waiting_conn_ids.remove(player_conn_id)
            player = connection_manager.get_player(player_conn_id)
            send_data(
                player.conn,
                game_manager.get_game(game_id).state + ':' + str(player.player_side)
            )

        print('Current queue:', self.waiting_conn_ids)
        return True


queue_manager = QueueManager()
