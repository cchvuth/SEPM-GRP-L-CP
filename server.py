import os
from dotenv import load_dotenv
import traceback
import socket
from _thread import *
import uuid
from connection_manager import connection_manager
from queue_manager import queue_manager
from transfer_protocol import send_data
from menu import main_menu

load_dotenv()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIp = os.getenv('SERVER_IP')
serverPort = os.getenv('SERVER_PORT')

try:
    server.bind((serverIp, int(serverPort)))
except socket.error as e:
    str(e)

queue_manager.mode = main_menu()

server.listen(2)
print('Server Started on', serverIp + ':' + serverPort + '.', 'Listening for client conns...')

while True:
    try:
        # Accept client
        conn, addr = server.accept()

        if queue_manager.tournament_started:
            print('Tournament has already started. Rejecting new connection') 
            send_data(conn, 'tournament_started') 
            conn.close()     
            continue 
        
        if connection_manager.conn_counts >= 8:
            print('Server is full :(') 
            send_data(conn, 'server_full') 
            conn.close()     
            continue 

        connection_manager.increment_conn_counts()

        print('Conn accepted from:', addr)

        # Handle player connection
        start_new_thread(connection_manager.handle_conn, (conn, addr, str(uuid.uuid1())))
    except Exception:
        traceback.print_exc()
        break
