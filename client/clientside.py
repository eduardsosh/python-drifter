import socket
import json
import threading
import time

# Server IP and Port
SERVER_IP = '45.93.138.56'
SERVER_PORT = 55000

# Client's player ID and initial coordinates
player_id = "player1"
car_coordinates = {"x": 0, "y": 0}

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Flag to control the main loop
running = True

def send_coordinates():
    global running
    while running:
        try:
            # Simulate car movement
            car_coordinates["x"] += 1
            car_coordinates["y"] += 1

            # Prepare and send data to the server
            data = json.dumps({"player_id": player_id, "coordinates": car_coordinates})
            client_socket.sendto(data.encode(), (SERVER_IP, SERVER_PORT))

            # Wait before sending the next update
            time.sleep(1)
        except Exception as e:
            print(f"Error sending data: {e}")
            running = False

def receive_updates():
    global running
    while running:
        try:
            # Receive data from the server
            data, _ = client_socket.recvfrom(1024)
            print("Received data:", data.decode())
        except Exception as e:
            print(f"Error receiving data: {e}")
            running = False

def start_client():
    # Start a thread to send coordinates
    sender_thread = threading.Thread(target=send_coordinates)
    sender_thread.start()

    # Start a thread to receive updates
    receiver_thread = threading.Thread(target=receive_updates)
    receiver_thread.start()

    # Wait for threads to finish
    sender_thread.join()
    receiver_thread.join()
    client_socket.close()

if __name__ == "__main__":
    start_client()
