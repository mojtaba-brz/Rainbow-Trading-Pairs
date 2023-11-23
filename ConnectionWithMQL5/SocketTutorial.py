# Ref : https://realpython.com/python-sockets/

import socket

# To better understand this, check out the sequence of socket API calls and data flow for TCP :
# https://commons.wikimedia.org/wiki/File:InternetSocketBasicDiagram_zhtw.png

class SimpleServer():
    def __init__(self, host = '127.0.0.1', port = 65333, n_backlogs = 10):   
        self.host = host
        self.port = port
        self.n_backlogs = n_backlogs
    
    def print_and_echo(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))  # declares the roll of this bot as a server
            sock.listen(self.n_backlogs)
            
            conn, addr = sock.accept() # wait for a client
            print(f"connected to {addr}")
            while True:
                data = conn.recv(10000000)
                if not data:
                    break
                print(data)
                conn.sendall(data)
    
    def run_server(self):
        while True:
            self.print_and_echo()
            
if __name__ == '__main__':
    server = SimpleServer()
    server.run_server()