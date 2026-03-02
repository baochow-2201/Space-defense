import cv2

cap = cv2.VideoCapture("./assets/videos/intro2.0.mp4")
if not cap.isOpened():
    print("Không mở được video")
else:
    print("Video mở được")
cap.release()
