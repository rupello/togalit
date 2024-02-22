import streamlit as st
import time

# Initialize session state variables
if 'timer_seconds' not in st.session_state:
    st.session_state.timer_seconds = 10

if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 10

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
        reset_timer()
elif st.session_state.timer_state == "paused":
    progress_update()
    st.rerun()
