import socket
import threading
import json
import os
import glob

SERVER_IP = '45.93.138.56'
SERVER_PORT = 55000
ADDR = (SERVER_IP, SERVER_PORT)

# Define server commands:
DISCONNECT = "!DISCONNECT"
REQUEST_FILES = "!REQUEST_FILES"
SEND_FILES = "!SEND_FILES"
ACK = "!ACK"
BUFFER_SIZE = 1024


def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect(ADDR)
    except Exception as e:
        print(e)
        return None
    finally:
        print("Connected to server")
    return client

"""
Send file protocol:
1. Client sends SEND_FILES command
2. Server sends ACK
3. Client sends file name and size as json
4. Server sends ACK
5. Client sends file
6. Server sends ACK
7. Client sends ACK
8. Server sends DISCONNECT
"""

def send_file_to_server(filepath):
    try:
        conn = connect()
        if conn is None:
            return
        #1.
        conn.send(SEND_FILES.encode())
        #2.
        response = conn.recv(BUFFER_SIZE).decode()
        if response != ACK:
            raise Exception("Server did not respond with ACK")
        
        data_dict = {"file_name": filepath, "file_size": os.path.getsize(filepath)}
        #3.
        conn.send(json.dumps(data_dict).encode())
        
        #4.
        response = conn.recv(BUFFER_SIZE).decode()
        if response != ACK:
            raise Exception("Server did not respond with ACK")
        
        #5.
        with open(filepath, "rb") as f:
            bytes_read = f.read(BUFFER_SIZE)
            while bytes_read:
                conn.send(bytes_read)
                bytes_read = f.read(BUFFER_SIZE)
        
        #6.
        print("File sent, waiting for server ack")
        response = conn.recv(BUFFER_SIZE).decode()
        if response == ACK:
            print("Server responds with ack after file send")
        else:
            raise Exception("Server did not respond with ACK after file sent")
        
        
        #7.
        conn.send(ACK.encode())
    
    except Exception as e:
        print(e)
        return
    finally:
        response = conn.recv(BUFFER_SIZE).decode()
        if response != DISCONNECT:
            raise Exception("Server did not respond with DISCONNECT")
        print("closing connection")
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


def get_files_from_server():
    conn = connect()
    if conn is None:
        return
    
    try:
        conn.send(REQUEST_FILES.encode())
        
        response = conn.recv(BUFFER_SIZE).decode()
        file_data = json.loads(response)
        print("file data:",file_data)
        conn.send(ACK.encode())
        
        parent_dir = os.path.dirname(os.path.realpath(__file__))
        recording_dir = "recordings"
        if not os.path.exists(recording_dir):
            os.mkdir(recording_dir)
        
        
        for file_name, file_size in file_data.items():
            print(f"Receiving {file_name} ({file_size} bytes)")
            with open(os.path.join(recording_dir,file_name), "wb") as f:
                bytes_recieved = 0
                bytes_read = conn.recv(BUFFER_SIZE)
                while bytes_read:
                    f.write(bytes_read)
                    bytes_recieved += len(bytes_read)
                    if bytes_recieved == file_size:
                        break
                    bytes_read = conn.recv(BUFFER_SIZE)
            print("File received")
            conn.send(ACK.encode())
    
    except Exception as e:
        print(e)
        return
    finally:
        if conn.recv(BUFFER_SIZE).decode() != DISCONNECT:
            raise Exception("Server did not send DISCONNECT")
        conn.close()
    
