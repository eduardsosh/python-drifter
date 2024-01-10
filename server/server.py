import socket
import threading
import json
import os
import glob
import time

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 55000
ADDR = (SERVER_IP, SERVER_PORT)

# Define server commands:
DISCONNECT = "!DISCONNECT"
REQUEST_FILES = "!REQUEST_FILES"
SEND_FILES = "!SEND_FILES"
ACK = "!ACK"
BUFFER_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Creates a dictionary of pickles in current dir
def get_file_dict():
    files = glob.glob("*.pkl")
    data_dict = {}
    for file in files:
        data_dict[file] = os.path.getsize(file)
        
    return data_dict
        
        



"""
Send file protocol:
1. Client sends SEND_FILES command
2. Server sends ACK
3. Client sends file name and size as json
4. - Server sends ACK
5. Client sends file
6. Server sends ACK
7. Client sends ACK
8. Server sends DISCONNECT
"""

# Client wants to send files
def send_files(conn):
    try:
        conn.send(ACK.encode())
        #3.
        data = conn.recv(BUFFER_SIZE).decode()
        data = json.loads(data)
        file_name = data["file_name"]
        file_size = data["file_size"]

        # 4.
        #conn.send(ACK.encode())
        print(f"Receiving {file_name} ({file_size} bytes)")
        
        #5.
        with open(file_name, "wb") as f:
            data_recieved = 0
            bytes_read = conn.recv(BUFFER_SIZE)
            print("Receiving file..." + str(bytes_read))
            while bytes_read:
                f.write(bytes_read)
                data_recieved += len(bytes_read)
                if data_recieved == file_size:
                    break
                bytes_read = conn.recv(BUFFER_SIZE)

        #6.
        print("File received")
        conn.send(ACK.encode())

        # 7.
        data = conn.recv(BUFFER_SIZE).decode()
        if data == ACK:
            print("File transfer confirmed by client")
        else:
            print("File transfer not confirmed by client")

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        conn.send(DISCONNECT.encode())
        conn.close()

"""
Receive files protocol:
1. Client send REQUEST_FILES command
2. Server sends json with file data
3. Client sends ACK
4. Server sends files
4a client sends ACK
5. Server sends DISCONNECT
"""

# Client wants to receive files
def receive_files(conn):
    try:
        file_data = get_file_dict()
        file_json = json.dumps(file_data)
        # 2.
        conn.send(file_json.encode())
        
        # 3.
        response = conn.recv(BUFFER_SIZE).decode()
        if response == ACK:
            print("File data sent")
        else:
            raise Exception("File data not sent")
        
        # 4.
        for file_name, file_size in file_data.items():
            print(f"Sending {file_name} ({file_size} bytes)")
            
            with open(file_name, "rb") as f:
                bytes_read = f.read(BUFFER_SIZE)
                while bytes_read:
                    conn.send(bytes_read)
                    bytes_read = f.read(BUFFER_SIZE)
            print("File sent")
            # 4a.
            response = conn.recv(BUFFER_SIZE).decode()
            if response == ACK:
                print("Single file transfer confirmed by client")
            else:
                raise Exception("Single file transfer not confirmed by client")
            
        
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        # 5.
        conn.send(DISCONNECT.encode())
        conn.close()
    
        
        



def handle(conn, addr):
    print(f"{addr} connected.")
    
    connected = True
    while connected:
        data = conn.recv(1024).decode()
        print(f"Received {data} from {addr}")
        if data == DISCONNECT:
            connected = False
        elif data == REQUEST_FILES:
            print("Sending files...")
            receive_files(conn)
            connected = False
        elif data == SEND_FILES:
            conn.send(ACK.encode())
            print("Receiving files...")
            send_files(conn)
            connected = False



def start():
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")
    server.listen()
    while True:
        try:
            conn, addr = server.accept()
        except KeyboardInterrupt:
            print("Closing server")
            break
        thread = threading.Thread(target=handle, args=(conn, addr))
        thread.start()
        print(f"Active connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    start()