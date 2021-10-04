def send_data(conn, message):
    print('sending:', message)
    return conn.sendall(str.encode(str(message)))


def receive_data(conn):
    return conn.recv(1024 * 4).decode()
