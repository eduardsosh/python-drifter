import socket
import os

# Define the server's IP address and port
SERVER_HOST = '45.93.138.56'
SERVER_PORT = 55000
BUFFER_SIZE = 1024

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Send command to the server
command = input("Enter command (UPLOAD/GET_ALL): ").strip()
client_socket.sendall(command.encode())

if command == 'UPLOAD':
    # Specify the file path
    file_path = 'path_to_your_pickle_file.pkl'

    # Send the file
    with open(file_path, 'rb') as f:
        data = f.read()
        client_socket.sendall(str(len(data)).encode())
        client_socket.recv(BUFFER_SIZE)  # Wait for acknowledgement
        client_socket.sendall(data)

elif command == 'GET_ALL':
    # Receive the number of pickle files
    num_files = int(client_socket.recv(BUFFER_SIZE).decode())

    for _ in range(num_files):
        # Receive and save the pickle file
        with open(f'received_{i}.pkl', 'wb') as f:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
        client_socket.sendall(b'ACK')  # Send acknowledgement

# Close the connection
client_socket.close()
