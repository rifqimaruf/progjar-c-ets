# file_client_cli.py
import socket
import json
import base64
import logging
import time
import os

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    try:
        logging.warning(f"Sending command: {command_str}")
        sock.sendall(command_str.encode())
        data_received = ""
        while True:
            data = sock.recv(4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        return json.loads(data_received)
    except Exception as e:
        logging.error(f"Error during data transfer: {e}")
        return False
    finally:
        sock.close()

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("Daftar file:")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    start_time = time.time()
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        os.makedirs('downloaded_files', exist_ok=True)
        with open(f"downloaded_files/{namafile}", 'wb+') as fp:
            fp.write(isifile)
        end_time = time.time()
        file_size = len(isifile)
        duration = end_time - start_time
        throughput = file_size / duration if duration > 0 else 0
        return True, duration, throughput
    else:
        print("Gagal")
        return False, 0, 0

def remote_upload(filename=""):
    start_time = time.time()
    try:
        filepath = os.path.join('files', filename)  
        if not os.path.exists(filepath):
            print(f"File {filepath} tidak ditemukan")
            return False, 0, 0
        with open(filepath, 'rb') as fp:
            isifile = base64.b64encode(fp.read()).decode()
        command_str = f"UPLOAD {filename} {isifile}"
        hasil = send_command(command_str)
        if hasil and hasil['status'] == 'OK':
            end_time = time.time()
            file_size = os.path.getsize(filepath)
            duration = end_time - start_time
            throughput = file_size / duration if duration > 0 else 0
            return True, duration, throughput
        else:
            print("Gagal")
            return False, 0, 0
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return False, 0, 0

if __name__ == '__main__':
    server_address = ('0.0.0.0', 7777)
    remote_list()
    remote_get('10mb.mp4')
    remote_upload('10mb.mp4')