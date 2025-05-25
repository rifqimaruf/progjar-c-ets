# file_protocol.py
import json
import logging
import shlex
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"Processing string: {string_datamasuk}")
        c = shlex.split(string_datamasuk)
        try:
            c_request = c[0].strip().lower()
            logging.warning(f"Processing request: {c_request}")
            params = c[1:]
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except Exception:
            return json.dumps(dict(status='ERROR', data='Request not recognized'))

if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET 10mb.mp4"))
    print(fp.proses_string("UPLOAD 10mb.mp4 " + base64.b64encode(b'test data').decode()))