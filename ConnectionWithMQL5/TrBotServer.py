import time
import numpy as np
import socketserver

# Local Imports =========================
from ConnectionWithMQL5.typedefs import *
from ConnectionWithMQL5.MessagesLib import default_decoder, default_encoder

class TrBotServerHandler(socketserver.BaseRequestHandler):

    # Configs =============================================================================================================================
    # =====================================================================================================================================
    name = "Server"
    mql_time_out_limit = 100.
    py_time_out_limit  = 100.
    # =====================================================================================================================================
    
    last_pyClient_message_time = [0.]
    last_mqlClient_message_time = [0.]
    
    algo_params = [0.]
    
    pyClient_last_requested_action_data = [b'']
    market_states = [b'']
    
    def handle(self):
        data = self.request.recv(10000).strip(); #print(data)
        if data:
            decoded_data = default_decoder(data)[0]
            
            # =====================================================================================================================================          
            # =====================================================================================================================================          
            # =====================================================================================================================================          
            if "PY" in decoded_data.name:
                self.last_pyClient_message_time[0] = time.time()
                if decoded_data.message_type == MESSAGE_TYPE.ACTION:
                    self.pyClient_last_requested_action_data[0] = data
                if decoded_data.message_type == MESSAGE_TYPE.REQUEST_MESSAGE:
                    while(self.market_states[0]):
                        self.request.send(self.market_states[0])
                        self.market_states[0] = b''                    
                elif decoded_data.message_type == MESSAGE_TYPE.CONNECTION_CHECK:
                    data = default_encoder(self.name, MESSAGE_TYPE.CONNECTION_CHECK.value, 
                                           "1" if time.time()-self.last_mqlClient_message_time[0] < self.mql_time_out_limit else "0") 
                    self.request.send(data)
                elif decoded_data.message_type == MESSAGE_TYPE.SAY_HELLO:
                    print(f"t = {time.time():>.0f}, HF PY")
                elif decoded_data.message_type == MESSAGE_TYPE.ALGO_PARAMS:
                    if self.algo_params[0] != 0. :
                        self.request.send(self.algo_params[0])
            
            # =====================================================================================================================================          
            # =====================================================================================================================================          
            # =====================================================================================================================================          
            elif "Mql" in decoded_data.name:
                self.last_mqlClient_message_time[0] = time.time()
                if decoded_data.message_type == MESSAGE_TYPE.MARKET_STATES:
                    self.market_states[0] = data
                    if len(self.market_states) > 10:
                        self.market_states.pop(0)
                    
                if decoded_data.message_type == MESSAGE_TYPE.ACTION:
                        self.request.send(self.pyClient_last_requested_action_data[0]) 
                        self.pyClient_last_requested_action_data[0] = b'';
                elif decoded_data.message_type == MESSAGE_TYPE.CONNECTION_CHECK:
                    data = default_encoder(self.name, MESSAGE_TYPE.CONNECTION_CHECK.value, 
                                           "1" if time.time()-self.last_pyClient_message_time[0] < self.py_time_out_limit else "0")  
                    self.request.send(data)  
                elif decoded_data.message_type == MESSAGE_TYPE.SAY_HELLO:
                    print(f"t = {time.time():>.0f}, HF MQL")
                elif decoded_data.message_type == MESSAGE_TYPE.ALGO_PARAMS:
                    self.algo_params[0] = data
                    
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
class TrBotServer():
    def __init__(self, host = "127.0.0.1", port = 65333):
        self.host = host
        self.port = port
        self.server = socketserver.TCPServer((host, port), TrBotServerHandler)
        # self.server.timeout = 1
    def run_tr_bot_server(self):
         self.server.serve_forever()
    
    def __del__(self):
        self.server.shutdown()
        self.server.server_close()
    
if __name__ == "__main__":
    # take unit tests
    tbs = TrBotServer()
    tbs.run_tr_bot_server()