import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import sys
import time
import winsound  # Import the winsound library for the alarm

# --- Alarm Configuration ---
ALARM_SOUND_PATH = "alarm.wav"
DETECTION_THRESHOLD = 0  # Trigger alarm if more than 0 objects are detected

model = YOLO('B+.pt')

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open webcam")
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

def play_alarm():
    """Play the alarm sound asynchronously."""
    winsound.PlaySound(ALARM_SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)

def stop_alarm():
    """Stop the alarm sound."""
    winsound.PlaySound(None, winsound.SND_ASYNC)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot read frame")
        break

    frame_resized = cv2.resize(frame, (416, 416))
    results = model(frame_resized, stream=False)
    annotated_frame = results[0].plot()
    detected_count = len(results[0].boxes)

    # --- Alarm Logic ---
    if detected_count > DETECTION_THRESHOLD:
        if not alarm_on:
            play_alarm()
            alarm_on = True
    else:
        if alarm_on:
            stop_alarm()
            alarm_on = False

    frame_index += 1
    x_data.append(detected_count)
    y_data.append(frame_index) # Swapped for correct plotting
    if len(y_data) > 100:
        y_data.pop(0)
        x_data.pop(0)

    line.set_data(y_data, x_data) # Swapped for correct plotting
    ax.set_xlim(max(0, frame_index-100), frame_index)
    ax.set_ylim(0, max(20, max(x_data) + 5 if x_data else 0))
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.001)

    cv2.imshow("YOLOv8 Live Feed", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
plt.close(fig)
stop_alarm() # Ensure alarm is off when script ends