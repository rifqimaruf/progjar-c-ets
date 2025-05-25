# file_server.py
from socket import *
import socket
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def process(self):
        try:
            while True:
                data = self.connection.recv(4096)  
                if data:
                    d = data.decode()
                    logging.warning(f"Received from {self.address}: {d}")
                    hasil = fp.proses_string(d)
                    hasil = hasil + "\r\n\r\n"
                    self.connection.sendall(hasil.encode())
                else:
                    break
        except Exception as e:
            logging.error(f"Error processing client {self.address}: {e}")
        finally:
            self.connection.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=7777, max_workers=5, pool_type='thread'):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool_type = pool_type
        self.max_workers = max_workers
        self.executor = None

    def start(self):
        logging.warning(f"Server running at {self.ipinfo} with {self.pool_type} pool, max_workers={self.max_workers}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(10)  # Increased backlog
        if self.pool_type == 'thread':
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        elif self.pool_type == 'process':
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        
        while True:
            try:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Connection from {client_address}")
                client_handler = ProcessTheClient(connection, client_address)
                self.executor.submit(client_handler.process)
            except Exception as e:
                logging.error(f"Server error: {e}")

def main(max_workers=5, pool_type='thread'):
    svr = Server(ipaddress='0.0.0.0', port=7777, max_workers=max_workers, pool_type=pool_type)
    svr.start()

if __name__ == "__main__":
    import sys
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    pool_type = sys.argv[2] if len(sys.argv) > 2 else 'thread'
    logging.basicConfig(level=logging.WARNING)
    main(max_workers, pool_type)
from socket import *
import socket
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address

    def process(self):
        try:
            while True:
                data = self.connection.recv(4096)  
                if data:
                    d = data.decode()
                    logging.warning(f"Received from {self.address}: {d}")
                    hasil = fp.proses_string(d)
                    hasil = hasil + "\r\n\r\n"
                    self.connection.sendall(hasil.encode())
                else:
                    break
        except Exception as e:
            logging.error(f"Error processing client {self.address}: {e}")
        finally:
            self.connection.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=7777, max_workers=5, pool_type='thread'):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool_type = pool_type
        self.max_workers = max_workers
        self.executor = None

    def start(self):
        logging.warning(f"Server running at {self.ipinfo} with {self.pool_type} pool, max_workers={self.max_workers}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(10) 
        if self.pool_type == 'thread':
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        elif self.pool_type == 'process':
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        
        while True:
            try:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Connection from {client_address}")
                client_handler = ProcessTheClient(connection, client_address)
                self.executor.submit(client_handler.process)
            except Exception as e:
                logging.error(f"Server error: {e}")

def main(max_workers=5, pool_type='thread'):
    svr = Server(ipaddress='0.0.0.0', port=7777, max_workers=max_workers, pool_type=pool_type)
    svr.start()

if __name__ == "__main__":
    import sys
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    pool_type = sys.argv[2] if len(sys.argv) > 2 else 'thread'
    logging.basicConfig(level=logging.WARNING)
    main(max_workers, pool_type)