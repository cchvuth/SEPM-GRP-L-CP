from connection_manager import connection_manager
from queue_manager import queue_manager
from _thread import *
from PyInquirer import prompt
import os


def open_tournament():
    input('Press enter to start the tournament. (Once started, no more player can join)\n')
    print('Starting matchmaking for', connection_manager.conn_counts, 'players')

    queue_manager.tournament_started = True

    while queue_manager.start_game():
        pass

    if connection_manager.conn_counts < 2:
        print('Too little number of players')
        os._exit(1)


def main_menu():
    questions = [
        {
            'type': 'list',
            'name': 'mode',
            'message': 'Please select server mode:',
            'choices': [
                {
                    'name': 'Play against other player',
                    'value': 'play-against-player',
                },
                {
                    'name': 'Play against AI',
                    'value': 'ai'
                },
                {
                    'name': 'Tournament',
                    'value': 'tournament'
                }
            ]
        }
    ]

    answers = prompt(questions)
    mode = answers['mode']

    print('You have selected', mode, 'mode')

    if mode in ['tournament', 'play-against-player']:
        start_new_thread(open_tournament, ())

    return mode
