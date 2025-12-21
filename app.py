import streamlit as st
import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import numpy as np
from playsound import playsound
import threading

# --- Page Configuration ---
st.set_page_config(
    page_title="Theft & Anomaly Detection",
    page_icon="🤖",
    layout="wide",
)

# --- Alarm Configuration ---
ALARM_SOUND_PATH = "alarm.wav"
DETECTION_THRESHOLD = 0

# --- Alarm Function ---
def play_alarm_sound():
    """Plays the alarm sound in a separate thread."""
    try:
        playsound(ALARM_SOUND_PATH)
    except Exception as e:
        print(f"Error playing sound: {e}")

# --- Model ---
@st.cache_resource
def load_model():
    return YOLO('B+.pt')

model = load_model()

# --- About Page Content ---
def about_page():
    st.header("About This Project")
    st.markdown("""
    This application is a real-time **Theft and Anomaly Detection System** designed to identify and alert users to potential threats. By leveraging the power of computer vision and deep learning, it provides a robust solution for automated surveillance.
    """)

    st.subheader("Core Technology")
    st.markdown("""
    - **Model:** The system is powered by a custom-trained **YOLOv8 (You Only Look Once, version 8)** model. YOLO is a state-of-the-art, real-time object detection algorithm known for its exceptional speed and accuracy.
    - **Framework:** The user interface is built with **Streamlit**, an open-source Python library that makes it easy to create beautiful, custom web apps for machine learning and data science.
    """)

    st.subheader("Key Features")
    st.markdown("""
    - **Live Webcam Detection:** Directly access your webcam for real-time monitoring and object detection.
    - **Video File Analysis:** Upload pre-recorded video files to analyze past events.
    - **Audible Alarms:** An integrated alarm system provides immediate audio alerts when an object is detected, ensuring prompt notification.
    - **Real-time Analytics:** A dynamic chart visualizes the number of detected objects over time, offering insights into activity levels.
    """)

# --- Main App ---
st.title("Theft & Anomaly Detection")

app_mode = st.sidebar.selectbox("Choose a mode", ["About Project", "Live Detection", "Video Detection"])

# Initialize session state for the alarm
if 'alarm_on' not in st.session_state:
    st.session_state.alarm_on = False

if app_mode == "About Project":
    about_page()

elif app_mode == "Live Detection":
    st.header("Live Feed Detection")
    run_live = st.checkbox("Start Webcam")
    frame_placeholder = st.empty()
    chart_placeholder = st.empty()

    if run_live:
        cap = cv2.VideoCapture(0)
        fig, ax = plt.subplots()
        x_data, y_data = [], []
        line, = ax.plot([], [], 'r-', linewidth=2)
        frame_index = 0

        while run_live:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to grab frame from webcam.")
                break

            results = model(cv2.resize(frame, (416, 416)), stream=False)
            annotated_frame = results[0].plot()
            detected_count = len(results[0].boxes)

            if detected_count > DETECTION_THRESHOLD:
                if not st.session_state.alarm_on:
                    st.session_state.alarm_on = True
                    threading.Thread(target=play_alarm_sound).start()
            else:
                st.session_state.alarm_on = False

            frame_index += 1
            x_data.append(frame_index)
            y_data.append(detected_count)
            line.set_data(x_data, y_data)
            ax.set_xlim(max(0, frame_index - 100), frame_index)
            ax.set_ylim(0, max(20, max(y_data) + 5 if y_data else 0))

            frame_placeholder.image(annotated_frame, channels="BGR")
            chart_placeholder.pyplot(fig)
        
        cap.release()
        plt.close(fig)

elif app_mode == "Video Detection":
    st.header("Video File Detection")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

    if uploaded_file:
        video_path = f"temp_{uploaded_file.name}"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.video(video_path)
        
        if st.button("Start Detection on Uploaded Video"):
            cap = cv2.VideoCapture(video_path)
            frame_placeholder = st.empty()
            chart_placeholder = st.empty()
            fig, ax = plt.subplots() 
            x_data, y_data = [], []
            line, = ax.plot([], [], 'b-', linewidth=2)
            frame_index = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    st.success("Video processing complete.")
                    break
                
                results = model(cv2.resize(frame, (416, 416)), stream=False)
                annotated_frame = results[0].plot()
                detected_count = len(results[0].boxes)

                if detected_count > DETECTION_THRESHOLD:
                    if not st.session_state.alarm_on:
                        st.session_state.alarm_on = True
                        threading.Thread(target=play_alarm_sound).start()
                else:
                    st.session_state.alarm_on = False

                frame_index += 1
                x_data.append(frame_index)
                y_data.append(detected_count)
                line.set_data(x_data, y_data)
                ax.set_xlim(max(0, frame_index - 100), frame_index)
                ax.set_ylim(0, max(20, max(y_data) + 5 if y_data else 0))

                frame_placeholder.image(annotated_frame, channels="BGR")
                chart_placeholder.pyplot(fig)

            cap.release()
            plt.close(fig)