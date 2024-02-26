from subprocess import Popen, PIPE
import socket
from contextlib import closing
from threading import Thread
import os
import sys
import logging

import streamlit


def find_free_port() -> str:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return str(s.getsockname()[1])


def findexe(root:str, try_names):
    logging.info(f"finding {try_names} under {root}...")
    for folder, _, files in os.walk(root):
        for file in files:
            full_path = os.path.join(folder, file)
            if os.access(full_path, os.X_OK):
                if file.lower() in try_names:
                    return full_path
    raise Exception(f"could not find {try_names} under {root}")


def find_streamlit() -> str:
    """
        find the 'streamlit' executable 
            note: running as a module (eg python -m streamlit) works in dev
            but installed version has no 'python' cmd and 'sys.executable' 
            will re-spawn the main app
    """
    packaged_root = os.path.dirname(os.path.dirname(streamlit.__file__)) 
    dev_root = os.path.dirname(sys.executable)
    for root in [packaged_root, dev_root]:
        try: 
            return findexe(root,try_names=['streamlit','streamlit.exe'])
        except Exception as ex:
            logging.info(ex)
    raise Exception(f"could not find streamlit exe under any root...")
    

class StreamlitCtrl(Thread):
    _started_streamlit:bool = False    
    _port:str = ''
    _proc:Popen = None
    _script:str = ''    
    _env = {}

    def __init__(self, script, env_vars={}):
        self._script = script
        self._env = env_vars # merge extra env vars
        super().__init__()

    def signal_shutdown(self):
        self._proc.terminate()

    def started(self):
        return self._started_streamlit
    
    def is_shutdown(self):
        return self._is_shutdown
    
    def port(self):
        return self._port

    def run(self):
        # pass through environment + extra path vars
        st_env = os.environ.copy()
        st_env = st_env | self._env
        self._port = find_free_port()
        cmd = find_streamlit()
        logging.info(f'starting {cmd}...')
        self._proc = Popen(args=[
            cmd,                                
            'run', 
            self._script,
            '--server.port', self._port,
            ], 
            stdout=PIPE, 
            stderr=PIPE,
            env=st_env)

        for line in self._proc.stdout:
            logging.info(line.decode())
            if line.decode('utf-8').find('Streamlit') >= 0:
                self._started_streamlit = True