import socket
import os
import pickle

# Define the server's IP address and port
SERVER_HOST = '45.93.138.56'
SERVER_PORT = 55000
BUFFER_SIZE = 1024

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")


def send_all_pickles(client_socket, BUFFER_SIZE=1024):
    pickle_files = [f for f in os.listdir() if f.endswith('.pkl')]
    
    client_socket.sendall(str(len(pickle_files)).encode())

    client_socket.recv(BUFFER_SIZE)

    for file in pickle_files:
        client_socket.sendall(file.encode())
        client_socket.recv(BUFFER_SIZE)

        with open(file, 'rb') as f:
            data = f.read()
            client_socket.sendall(data)

        client_socket.recv(BUFFER_SIZE)


def receive_pickle(client_socket):
    # Receive the size of the incoming file
    file_size = int(client_socket.recv(BUFFER_SIZE).decode())

    # Receive the file
    with open('received_file.pkl', 'wb') as f:
        remaining = file_size
        while remaining:
            data = client_socket.recv(min(BUFFER_SIZE, remaining))
            if not data: break
            f.write(data)
            remaining -= len(data)

while True:
    # Accept a connection
    client_socket, client_address = server_socket.accept()
    print(f"Connected to {client_address}")

    # Receive the command from the client
    command = client_socket.recv(BUFFER_SIZE).decode()

    if command == 'UPLOAD':
        receive_pickle(client_socket)
    elif command == 'GET_ALL':
        send_all_pickles(client_socket)

    # Close the connection
    client_socket.close()
