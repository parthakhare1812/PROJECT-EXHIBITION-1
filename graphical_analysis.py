import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections
import cv2
import threading
import time

class RealTimeGraph:
    def __init__(self, max_points=100):
        self.max_points = max_points
        self.fig, self.ax = plt.subplots()
        self.x_data = collections.deque(maxlen=max_points)
        self.y_data = collections.deque(maxlen=max_points)
        self.line, = self.ax.plot([], [], 'r-', linewidth=2)
        self.ax.set_xlim(0, max_points)
        self.ax.set_ylim(0, 20)
        self.ax.set_title("Detected Object Count Over Time")
        self.ax.set_xlabel("Frame")
        self.ax.set_ylabel("Count")
        self.frame_index = 0
        self.background = None

    def init(self):
        self.line.set_data([], [])
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)  # Save background for blitting
        return self.line,

    def update_plot(self, detected_count):
        self.frame_index += 1
        self.x_data.append(self.frame_index)
        self.y_data.append(detected_count)

    def animate(self, i):
        self.fig.canvas.restore_region(self.background)  # Restore background for faster redraw
        self.line.set_data(self.x_data, self.y_data)
        self.ax.draw_artist(self.line)
        self.fig.canvas.blit(self.ax.bbox)
        self.ax.set_xlim(max(0, self.frame_index - self.max_points), max(self.frame_index, self.max_points))
        return self.line,

    def run(self):
        self.ani = FuncAnimation(self.fig, self.animate, init_func=self.init,
                                 interval=30, blit=True)
        plt.show()

def video_capture_loop(graph, video_path=0):
    cap = cv2.VideoCapture(video_path)
    frame_skip = 2  # Skip some frames to speed up
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % frame_skip != 0:
            continue
        # Dummy detected count, replace with actual object detection logic
        detected_count = 10  # For example, some detection count from frame processing

        graph.update_plot(detected_count)

        # Show video with bounding boxes or annotations (dummy)
        cv2.putText(frame, f'Count: {detected_count}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.imshow('Video Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    graph = RealTimeGraph(max_points=100)
    video_thread = threading.Thread(target=video_capture_loop, args=(graph,))
    video_thread.start()
    graph.run()
    video_thread.join()
