import os
from dotenv import load_dotenv
import socket
from _thread import *
import sys
import traceback

load_dotenv()


class Client:
    def __init__(self, username):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = os.getenv('SERVER_IP')
        self.port = os.getenv('SERVER_PORT')
        self.username = username
        self.player_side = None
        self.client.connect((self.server, int(self.port)))

    def receive(self):
        return self.client.recv(1024 * 4).decode()

    def send(self, data, receive = True):
        try:
            self.client.send(str.encode(data))
            if receive: return self.receive()
        except socket.error as e:
            print(e)
            
    def register(self):
        try:
            self.player_side = self.send('register:' + self.username)
            return self.player_side
        except socket.error as e:
            print(e)
            sys.exit()

    def close(self):
        try:
            self.client.shutdown(socket.SHUT_WR)
            self.client.close()
        except:
            pass


print(os.getenv('SERVER_IP'), os.getenv('SERVER_PORT'))

# def ask_to_continue(player):
#     answer = input('Game Ended. Do you want to register for another match? (y/n)?\n')
#     if answer == 'y':
#         return True

#     player.close()
#     os._exit(1)


def game_ended(player):
    print('Game ended, Waiting for a new game')
    start_new_thread(wait_for_game, (player,))


def handle_input(player):
    answer = input('What do you want to send?\n')

    if answer == ':q':
        player.close()
        os._exit(1)
    
    try:        
        print('Sending', answer)
        player.send(answer, False)
        print('sent')
    except:
        print('failed to send')


def listen_for_message(player):
    print('Listening for messages')
    start_new_thread(handle_input, (player,))

    while True:
        try:
            received = player.receive()
            print('Received', received)
            if not received:
                break
            elif received == 'opponent_disconnected':
                print('Your opponent forfeited the match, you win!')
                print(player.receive())
                game_ended(player)
                break
            # received scoreboard, register for another match
            elif '{' in received:
                game_ended(player)
                break
        except Exception:
            traceback.print_exc()
            player.close()
            os._exit(1)


def wait_for_game(player):
    player_game_state = player.send('get_state')
    
    print('Game state:', player_game_state)
    if player_game_state == 'game_created' or player_game_state == 'registration_accepted':
        print('Waiting for a game')
        while True:
            received = player.receive()
            if not received:
                print('Error receiving, exiting')
                player.close()
                os._exit(1)
                break
            elif 'game_ready' in received:
                print('Game Ready, you\'re player:', received[11:])
                break
            elif received == 'tournament_ended':
                print('Tournament Ended')
                print('Final score:', player.receive())
                player.close()
                os._exit(1)
                break
    elif 'game_ready' in player_game_state:
        print('Game Ready, you\'re player:', player_game_state[11:])
    elif player_game_state == 'tournament_ended':
        print('Tournament Ended')
        print('Final score:', player.receive())
        player.close()
        os._exit(1)

    start_new_thread(listen_for_message, (player,))


def main():
    try:
        player = None
        registration = None
        
        while registration == None or registration == 'username_taken':
            username = input('Please enter your username:\n')

            if player == None:
                player = Client(username)
            else:
                player.username = username

            registration = player.register()
            print('Registration Status:', registration, '\n')

        wait_for_game(player)

        while True:
            pass
    except Exception:
        traceback.print_exc()
        os._exit(1)


main()
