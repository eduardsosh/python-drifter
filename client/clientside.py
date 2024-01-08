import socket
import os

SERVER_HOST = '45.93.138.56'
SERVER_PORT = 55000
BUFFER_SIZE = 1024



def get_all_runs():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(5)
    
    try:
        server_socket.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Serveris neatbild")
        return -1
    
    command = 'GET_ALL'
    server_socket.sendall(command.encode())

    server_socket.recv(BUFFER_SIZE)
    
    file_count = int(server_socket.recv(BUFFER_SIZE).decode())

    server_socket.sendall(b"ACK")

    for _ in range(file_count):
        filename = server_socket.recv(BUFFER_SIZE).decode()

        server_socket.sendall(b"ACK")

        data = server_socket.recv(BUFFER_SIZE)

        with open(filename, 'wb') as f:
            f.write(data)

        server_socket.sendall(b"ACK")

    server_socket.close()

    
        
def upload_run(filename):
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    filepath = os.path.join(parent_dir, "recordings", filename)

    print(filepath)
    if not os.path.exists(filepath):
        print("Fails neeksiste")
        return -1
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(5)
    
    try:
        server_socket.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print("Serveris neatbild")
        return -1
    
    command = 'UPLOAD'
    server_socket.sendall(command.encode())
    
    
    file_size = os.path.getsize(filepath)
    server_socket.sendall(str(file_size).encode())
    
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            server_socket.sendall(data)
            server_socket.recv(BUFFER_SIZE)  # Wait for acknowledgement
    server_socket.close()
    return 0
        
    
    

upload_run('recording20240107-195930.pkl')


    