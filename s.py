import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 25565))
server.listen(5)

while True:
    conn, addr = server.accept()
    print(f"Connection from {addr}")
    conn.send(b"Hello from server")
    conn.close()