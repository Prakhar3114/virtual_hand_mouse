import cv2
import mediapipe as mp
import pyautogui
import math
import threading
import tkinter as tk

# Global state variables
is_running = False
cap = None

# Initialize MediaPipe and Screen Size
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

# Gesture control loop
def gesture_control():
    global is_running, cap

    cap = cv2.VideoCapture(0)
    pinch_active = False

    while is_running:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                index_tip = lm[8]
                thumb_tip = lm[4]
                middle_tip = lm[12]

                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                mx, my = int(middle_tip.x * w), int(middle_tip.y * h)

                screen_x = int(index_tip.x * screen_width)
                screen_y = int(index_tip.y * screen_height)
                pyautogui.moveTo(screen_x, screen_y)

                pinch_distance = math.hypot(tx - ix, ty - iy)
                if pinch_distance < 30:
                    if not pinch_active:
                        pinch_active = True
                        pyautogui.mouseDown()
                else:
                    if pinch_active:
                        pinch_active = False
                        pyautogui.mouseUp()

                # Scroll
                if abs(iy - my) < 40 and abs(ix - mx) > 40:
                    scroll_value = int((ix - mx) / 10)
                    pyautogui.scroll(scroll_value)

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Virtual Mouse", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# GUI functions
def start_mouse_control():
    global is_running
    if not is_running:
        is_running = True
        threading.Thread(target=gesture_control).start()
        status_label.config(text="Status: Running")

def stop_mouse_control():
    global is_running
    is_running = False
    status_label.config(text="Status: Stopped")

# Setup GUI
root = tk.Tk()
root.title("Virtual Hand Mouse")
root.geometry("300x150")

tk.Label(root, text="Control Mouse with Hand Gestures", font=("Helvetica", 12)).pack(pady=10)
tk.Button(root, text="Start", command=start_mouse_control, width=10).pack(pady=5)
tk.Button(root, text="Stop", command=stop_mouse_control, width=10).pack(pady=5)
status_label = tk.Label(root, text="Status: Stopped", fg="blue")
status_label.pack(pady=10)

root.mainloop()
