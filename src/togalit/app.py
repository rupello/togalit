"""
 Toga App Wrapper
"""
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
import os
import logging

import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from dotenv import load_dotenv

from togalit.streamlitctrl import StreamlitCtrl

class ContainerApp(toga.App):
    
    _streamlit:StreamlitCtrl = None

    def __init__(self):
        super().__init__(on_exit=self.shutdown_streamlit)
        
    def start_streamlit(self):
        # user settings take preference...
        load_dotenv(dotenv_path=os.path.join(self._paths.config,"settings.env"), verbose=True)
        # baked-in defaults...
        load_dotenv(dotenv_path=os.path.join(self._paths.app,"resources/settings.env"), verbose=True)

        # script to run
        script_path:Path  = Path(os.path.join(self._paths.app, "st_script.py"))
        # pass the toga paths as env vars
        streamlit_env = {
            "PATH_APP": str(self._paths.app),
            "PATH_CACHE": str(self._paths.cache),
            "PATH_CONFIG": str(self._paths.config),
            "PATH_LOGS": str(self._paths.logs),
            "PATH_DATA": str(self._paths.data),
        }
        self._streamlit= StreamlitCtrl(script=script_path, env_vars=streamlit_env)
        self._streamlit.start()
        while not self._streamlit.started():
            time.sleep(.5)

    def init_logging(self):
        os.makedirs(self._paths.logs, exist_ok=True)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(os.path.join(self._paths.logs, 'container.log'), maxBytes=1024*100, backupCount=10)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logging.info(f"*** init logging ***")

    def startup(self):
        self.init_logging() 
        self.start_streamlit()

        main_box = toga.Box(style=Pack(direction=COLUMN))

        web_view = toga.WebView(
            url=f"http://127.0.0.1:{self._streamlit.port()}/",
            style=Pack(flex=1),
        )
        main_box.add(web_view)

        self.main_window = toga.MainWindow(title=self.formal_name, 
                                           size=(1000,618), position=(200,200))
        self.main_window.content = main_box
        self.main_window.show()


    def shutdown_streamlit(self, App):
        self._streamlit.signal_shutdown()
        self._streamlit.join()
        return True


def main():
    return ContainerApp()