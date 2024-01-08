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
    BUFFER_SIZE = 1024  # Define a suitable buffer size
    SERVER_HOST = 'your_server_host'  # Define server host
    SERVER_PORT = 12345  # Define server port

    # Constructing the file path
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    filepath = os.path.join(parent_dir, "recordings", filename)

    print(filepath)

    # Check if file exists
    if not os.path.exists(filepath):
        print("File does not exist")
        return -1

    # Initialize socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(5)  # Timeout for socket operations

    try:
        # Connect to server
        server_socket.connect((SERVER_HOST, SERVER_PORT))

        # Send upload command
        command = 'UPLOAD'
        server_socket.sendall(command.encode())

        # Send file size
        file_size = os.path.getsize(filepath)
        server_socket.sendall(str(file_size).encode())

        # Open file and start sending
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                server_socket.sendall(data)
                # Optionally wait for acknowledgment

        # Send a message to indicate file transfer completion
        server_socket.sendall(b"END_OF_FILE")

    except FileNotFoundError:
        print("File not found: " + filepath)
        return -1
    except ConnectionRefusedError:
        print("Server is not responding")
        return -1
    except socket.timeout:
        print("Socket operation timed out")
        return -1
    except socket.error as e:
        print("Socket error:", e)
        return -1
    except Exception as e:
        print("An unexpected error occurred:", e)
        return -1
    finally:
        # Ensure the socket is closed even if an error occurs
        server_socket.close()

    return 0
        
    
    

upload_run('recording20240107-195930.pkl')


    