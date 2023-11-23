# this script is written for test purposes only
import socket
import numpy as np
import time
import threading
import os

def clc():
    os.system('cls' if os.name == 'nt' else 'clear')
# Local Imports =========================
from ConnectionWithMQL5.typedefs import *
from ConnectionWithMQL5.MessagesLib import default_decoder, default_encoder, market_states_decoder

class TrBotPYSideClient():
    def __init__(self, host_addr = "127.0.0.1", host_port = 65333, hello_period = 10):
        self.name = "TrBotPYSideClient"
        self.host_addr = host_addr
        self.host_port = host_port
        self.connected_to_mql = False
        self.hello_period = hello_period
        
        say_hello_thread = threading.Thread(target = self.send_hello)
        say_hello_thread.start()
          
    def send_hello(self, forever = True):
        while(True):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.host_addr, self.host_port))
                    sock.settimeout(0.1)
                    sock.send(default_encoder(self.name, MESSAGE_TYPE.SAY_HELLO.value, ""))
            except:
                print("couldn't send hello to server")

            if not forever:
                break
            time.sleep(self.hello_period)
        
    def check_mql_client_connection(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_addr, self.host_port))
                sock.settimeout(0.1)
                sock.send(default_encoder(self.name, MESSAGE_TYPE.CONNECTION_CHECK.value, ""))
                
                sock.settimeout(1)
                data = sock.recv(10000)
                if data:
                    data = default_decoder(data)[0]
                    self.connected_to_mql = data.message == "1"
                else:
                    self.connected_to_mql = False
                return True
        except:
            return False
        
    def get_market_states_if_available(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_addr, self.host_port))
                sock.settimeout(0.1)
                sock.send(default_encoder(self.name, MESSAGE_TYPE.REQUEST_MESSAGE.value, ""))
                
                messages = ""
                sock.settimeout(1)
                while True:
                    data = sock.recv(10000)
                    if data:
                        default_messages = default_decoder(data)                
                        for dm in default_messages:
                            messages += dm.message
                    else:
                        break
                if messages:
                    market_states, reward_raw_data, done = market_states_decoder(messages)
                    return market_states, reward_raw_data, done
                else:
                    return None, None, None
        except:
            return None, None, None
        
    def send_action(self, action):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_addr, self.host_port))
                sock.settimeout(0.1)
                sock.send(default_encoder(self.name, MESSAGE_TYPE.ACTION.value, f"{action}"))
                return True
        except:
            return False
        
    def get_algo_params(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host_addr, self.host_port))
                sock.settimeout(0.1)
                sock.send(default_encoder(self.name, MESSAGE_TYPE.ALGO_PARAMS.value, ""))
                
                sock.settimeout(1)
                data = sock.recv(10000)
                if data:
                    data = default_decoder(data)[0]
                    self.algo_params_recieved = True
                    return data.message
                else:
                    self.algo_params_recieved = False
                    return False
        except:
            return False

# =======================================================================================
# =======================================================================================
# =======================================================================================   
if __name__ == "__main__":
    client = TrBotPYSideClient()

    while True:
        clc()
        time.sleep(0.1)
        print(client.check_mql_client_connection())
        print(client.get_market_states_if_available())
        print(client.send_action(TR_ACTIONS.SELL_NOW.value))
        print(client.get_algo_params())
        time.sleep(1.)
    