import socket
import threading
import json

# Server IP and Port
SERVER_IP = 'infoauto.lv'
SERVER_PORT = 12345

# Store car coordinates (player_id: coordinates)
car_coordinates = {}

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

def handle_client(client_address):
    while True:
        try:
            # Receive data from a client
            data, address = server_socket.recvfrom(1024)
            data = json.loads(data.decode())

            # Update the car coordinates
            car_coordinates[data['player_id']] = data['coordinates']

            # Broadcast updated coordinates to all clients
            for client in car_coordinates:
                server_socket.sendto(json.dumps(car_coordinates).encode(), client_address)
        except:
            break

def start_server():
    print("UDP Server listening on {}:{}".format(SERVER_IP, SERVER_PORT))
    while True:
        # Accept new connections
        data, client_address = server_socket.recvfrom(1024)
        print(f"New connection from {client_address}")

        # Start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_address,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
