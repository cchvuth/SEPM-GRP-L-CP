from player_manager import PlayerManager
from game_manager import game_manager
from queue_manager import queue_manager
from transfer_protocol import send_data, receive_data
from scoreboard_manager import scoreboard_manager


class ConnectionManager:
    def __init__(self):
        self.conn_counts = 0
        self.conn_map = {}

    def save_conn_info(self, username, conn, conn_id):
        for c_id, player in self.conn_map.items():
            if player.username == username:
                return False

        self.conn_map[conn_id] = PlayerManager(username, conn, conn_id)
        return self.conn_map[conn_id]

    def get_player(self, id):
        return self.conn_map[id]

    def increment_conn_counts(self, by = 1):
        self.conn_counts += by 

    def decrement_conn_counts(self, by = 1):
        self.conn_counts -= by

    def close_conn(self, id, clear_map = True):
        try:
            self.conn_map[id].conn.close()
        except:
            pass

        if clear_map: del self.conn_map[id] 
        self.decrement_conn_counts()
        print('Decrement connection counts', self.conn_counts)

    def handle_disconnection(self, conn_id):
        print('Lost connection with', conn_id)
        try:
            disconnected_player = self.get_player(conn_id)
        except:
            return
            
        game_id = disconnected_player.game_id

        if game_id is not None:
            try:
                opponent = self.get_player(game_manager.get_game(game_id).conn_ids[(disconnected_player.player_side + 1) % 2])

                score_file = scoreboard_manager.add_score(opponent.username, disconnected_player.username)

                opponent.leave_game()
                game_manager.decrement_player_in_game()

                send_data(opponent.conn, 'opponent_disconnected')
                send_data(opponent.conn, score_file)
            except:
                pass

            print('Closing game', game_id)
            game_manager.del_game(game_id)
            game_manager.decrement_player_in_game()
            
        self.close_conn(conn_id)

        while queue_manager.start_game():
            pass

    def handle_conn(self, conn, addr, conn_id):
        print('Handling', conn_id)
        while True:
            '''
            possible reply from server =
                    registration_accepted,
                    must_register,
                    username_taken,
                    game_ready:{player_side},
                    ok, winner, loser,
                    opponent_disconnected,
                    tournament_ended,
                    {any game data}

            possible command to server = 
                    register:{username},
                    get_state
                    winner (who sends win),
                    draw,
                    {any game data}
            '''

            data = receive_data(conn)
            print('Received', data, 'from:', conn_id, addr)

            if not data:
                self.handle_disconnection(conn_id)
                break
                
            if 'register' in data:
                username = data[9:]
                print('Registering', username)
                if self.save_conn_info(username, conn, conn_id):
                    queue_manager.add_player(conn_id)
                    send_data(conn, 'registration_accepted')
                else:
                    send_data(conn, 'username_taken')
            # player must register their username first
            elif conn_id in self.conn_map:
                player_info = self.get_player(conn_id)
                game_id = player_info.game_id

                if game_id in game_manager.active_games:
                    current_game = game_manager.get_game(game_id)

                    try:
                        opponent_info = self.get_player(current_game.conn_ids[(player_info.player_side + 1) % 2])
                    except:
                        opponent_info = None

                    if data == 'get_state':
                        send_data(conn, current_game.state)
                    elif data == 'winner':
                        game_manager.end_game(
                            game_id,
                            scoreboard_manager.add_score(player_info.username, opponent_info.username)
                        )
                    elif data == 'draw':
                        game_manager.end_game(
                            game_id,
                            scoreboard_manager.add_draw(player_info.username, opponent_info.username)
                        )
                    else:
                        current_game.state = data
                        send_data(conn, 'ok')
                        send_data(opponent_info.conn, data)
                else:
                    # handle_game_not_found
                    send_data(conn, 'registration_accepted')
            else:
                send_data(conn, 'must_register')
        print('Stop handling', conn_id)


connection_manager = ConnectionManager()
