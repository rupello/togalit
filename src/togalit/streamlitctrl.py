from subprocess import Popen, PIPE
import socket
from contextlib import closing
from threading import Thread
import os
import distutils.spawn

import streamlit


def find_free_port() -> str:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return str(s.getsockname()[1])
    
def find_streamlit() -> str:
    """
        find the 'streamlit' executable 
            note: running as a module (eg python -m streamlit) works in dev
            but installed version has no 'python' cmd and 'sys.executable' 
            will re-spawn the main app
    """
    print("finding streamlit...")
    try_paths = [
        distutils.spawn.find_executable("streamlit") or 'streamlit',                                        # find on path
        os.path.join(os.path.dirname(os.path.dirname(streamlit.__file__)),'bin/streamlit')   # packaged in site-packages/bin
    ]
    for p in try_paths:
        print(f"trying: {p}...")
        if os.path.exists(p):
            print(f"success")
            return p
    raise Exception(f"could not find streamlit in {try_paths}")


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
        print(f'starting {cmd}...')
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
            print(line.decode())
            if line.decode('utf-8').find('Streamlit') >= 0:
                self._started_streamlit = True