# file_interface.py
import os
import json
import base64
from glob import glob
import logging

class FileInterface:
    def __init__(self):
        os.makedirs('files', exist_ok=True) 
        os.chdir('files') 
        logging.warning("FileInterface initialized in directory: " + os.getcwd())

    def list(self, params=[]):
        try:
            filelist = glob('*.*')
            logging.warning(f"Listing files: {filelist}")
            return dict(status='OK', data=filelist)
        except Exception as e:
            logging.error(f"Error in list: {str(e)}")
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            logging.warning(f"Attempting to get file: {filename}")
            if not filename:
                return None
            if not os.path.exists(filename):
                logging.error(f"File {filename} does not exist")
                return dict(status='ERROR', data=f"File {filename} does not exist")
            with open(filename, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            logging.error(f"Error in get: {str(e)}")
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filedata = base64.b64decode(params[1])
            logging.warning(f"Uploading file: {filename}")
            os.makedirs('uploaded_files', exist_ok=True)
            with open(f'uploaded_files/{filename}', 'wb') as fp:
                fp.write(filedata)
            return dict(status='OK', data='File uploaded successfully')
        except Exception as e:
            logging.error(f"Error in upload: {str(e)}")
            return dict(status='ERROR', data=str(e))

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    f = FileInterface()
    print(f.list())
    print(f.get(['10mb.mp4']))
    print(f.upload(['10mb.mp4', base64.b64encode(b'test data').decode()]))