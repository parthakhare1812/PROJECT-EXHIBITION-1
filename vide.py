import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import sys
import time
from playsound import playsound
import threading

# --- Alarm Configuration ---
ALARM_SOUND_PATH = "alarm.wav"
DETECTION_THRESHOLD = 0 

model = YOLO('B+.pt')

# IMPORTANT: Make sure this video path is correct on your system
video_path = r"C:\Users\Partha\Desktop\project exhibition\video\Amateur MMA Fighter & Bodybuilder vs Kyokushin Karate Master - Saikou Karate (720p, h264).mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"ERROR: Could not open video file: {video_path}")
    sys.exit()

plt.ion()
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot([], [], 'r-', linewidth=2)
ax.set_xlim(0, 100)
ax.set_ylim(0, 20)
ax.set_title("Detected Object Count Over Time")
ax.set_xlabel("Frame")
ax.set_ylabel("Count")
frame_index = 0
alarm_on = False

def play_alarm_sound():
    """Plays the sound. Runs in a separate thread."""
    try:
        print("DEBUG: Attempting to play alarm.wav...")
        playsound(ALARM_SOUND_PATH)
        print("DEBUG: Alarm sound finished.")
    except Exception as e:
        print(f"ERROR: Could not play sound file. Make sure 'alarm.wav' is in the correct folder.")
        print(f"Error details: {e}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("INFO: End of video file.")
        break

    frame_resized = cv2.resize(frame, (416, 416))
    results = model(frame_resized, stream=False)
    annotated_frame = results[0].plot()
    detected_count = len(results[0].boxes)

    # --- New, More Robust Alarm Logic ---
    if detected_count > DETECTION_THRESHOLD:
        print(f"DEBUG: Violence detected! Count: {detected_count}")
        if not alarm_on:
            alarm_on = True # Set flag immediately to prevent re-triggering
            # Run the sound in a new thread so the video doesn't freeze
            threading.Thread(target=play_alarm_sound).start()
    else:
        # If the alarm was on, this resets it for the next detection event
        if alarm_on:
            print("DEBUG: Condition cleared. Resetting alarm flag.")
            alarm_on = False

    # --- Plotting and Display Logic (no changes here) ---
    frame_index += 1
    x_data.append(frame_index)
    y_data.append(detected_count)
    if len(x_data) > 100:
        x_data.pop(0)
        y_data.pop(0)

    line.set_data(x_data, y_data)
    ax.set_xlim(max(0, frame_index - 100), frame_index)
    ax.set_ylim(0, max(20, max(y_data) + 5 if y_data else 0))
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.001)

    cv2.imshow("YOLOv8 Video Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
plt.close(fig)
print("INFO: Script finished.")