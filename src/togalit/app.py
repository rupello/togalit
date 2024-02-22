"""
 Toga App Wrapper
"""
from pathlib import Path
import time
import os

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from togalit.streamlitctrl import StreamlitCtrl

class ContainerApp(toga.App):
    
    _streamlit:StreamlitCtrl = None

    def __init__(self):
        super().__init__(on_exit=self.shutdown_streamlit)
        
    def start_streamlit(self):
        # script to run
        script_path:Path  = Path(os.path.join(self._paths.app, "streamlit_main.py"))
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

    def startup(self):
        self.start_streamlit()

        main_box = toga.Box(style=Pack(direction=COLUMN))

        web_view = toga.WebView(
            url=f"http://127.0.0.1:{self._streamlit.port()}/",
            style=Pack(flex=1),
        )
        main_box.add(web_view)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


    def shutdown_streamlit(self, App):
        self._streamlit.signal_shutdown()
        self._streamlit.join()
        return True


def main():
    return ContainerApp()