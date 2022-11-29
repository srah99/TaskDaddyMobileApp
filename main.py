import socket
import threading

import port as port

HOST = socket.gethostbyname(socket.gethostname())  # dynamically assigns the addr
PORT = 2426

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST, port)

server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_connection(client):
    stop = False
    while not stop:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} left the chat.".encode('utf-8'),
                      stop = True)
def main():
    print("Server is working....")
    while True:
        client, addr = server.accept()
        print(f"Connected to {addr}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        clients.append(client)
        print(f"Nickname is {nickname}")

        broadcast(f"{nickname} joined the chat.")

        client.send("You are now connected.".encode('utf-8'))

        thread = threading.Thread(target=handle_connection(client,))
        thread.start()

        if __name__ == '__main__':
            main()