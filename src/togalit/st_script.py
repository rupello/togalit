from logging.handlers import RotatingFileHandler
import streamlit as st
import time
import os
import logging 


PATH_APP=os.environ['PATH_APP']
PATH_LOGS=os.environ['PATH_LOGS']

DEFAULT_TIMER=3

@st.cache_resource
def init_logging(log_name):
    """
        init fixed size rotating logs
    """
    os.makedirs(PATH_LOGS, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(os.path.join(PATH_LOGS,log_name), maxBytes=1024*100, backupCount=10)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.info(f"*** init logging ***")


init_logging('timer.log')

# test log messages
print("example message to standard out")
logging.debug("this logged to the logger")
logging.info("this logged to the logger")
logging.error("this logged to the logger")


# Initialize session state variables
if 'timer_seconds' not in st.session_state:
    st.session_state.timer_seconds = DEFAULT_TIMER

if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = DEFAULT_TIMER

if 'timer_state' not in st.session_state:
    st.session_state.timer_state = 'idle'


# Timer control functions
def start_timer():
    if st.session_state.timer_state == "idle":
        st.session_state.time_remaining = st.session_state.timer_seconds
    st.session_state.timer_state = "running"


def pause_timer():
    st.session_state.timer_state = "paused"


def reset_timer():
    st.session_state.timer_state = "idle"
    st.session_state.time_remaining = st.session_state.timer_seconds


def progress_update():
    # Progress bar
    st.progress(st.session_state.time_remaining / st.session_state.timer_seconds)
    st.text(f'{st.session_state.time_remaining}s remaining')
    time.sleep(1)


def sound_alert():
    try:
        # works on macOS
        os.system( "say 'times up!'" )
    except:
        pass


# App layout
st.title("Timer Demo")

# User sets the timer
st.session_state.timer_seconds = st.number_input("Set timer (in seconds):", min_value=0,
                                                 value=st.session_state.timer_seconds, key="set_timer")

# Timer buttons
col1, col2, col3 = st.columns(3)
with col1:
    st.button("Start", on_click=start_timer)
with col2:
    st.button("Pause", on_click=pause_timer)
with col3:
    st.button("Reset", on_click=reset_timer)

# Timer logic
if st.session_state.timer_state == "running":
    if st.session_state.time_remaining > 0:
        progress_update()
        st.session_state.time_remaining -= 1
        st.rerun()
    else:
        st.session_state.timer_running = False
        st.balloons()
        sound_alert()
        reset_timer()
elif st.session_state.timer_state == "paused":
    progress_update()
    st.rerun()
