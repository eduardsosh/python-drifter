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


def upload_run(filename):

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
