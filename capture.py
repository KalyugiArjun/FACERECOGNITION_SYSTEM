import cv2
import os
import sys
import time

# ==============================
# SAFE NAME HANDLING
# ==============================

if len(sys.argv) >= 2:
    name = sys.argv[1].strip().lower()
else:
    name = input("Enter Student Name: ").strip().lower()

if name == "":
    print("❌ Invalid Name")
    exit()

# ==============================
# CREATE DATASET FOLDER
# ==============================

path = os.path.join("dataset", name)
os.makedirs(path, exist_ok=True)

# Prevent overwrite – count existing images
existing_images = len(os.listdir(path))

# ==============================
# CAMERA INITIALIZATION
# ==============================

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("❌ Camera Not Detected")
    exit()

time.sleep(2)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

count = 0
max_images = 30

print("📷 Camera Started... Look at camera")

cv2.namedWindow("Face Capture", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Face Capture", cv2.WND_PROP_TOPMOST, 1)

# ==============================
# CAPTURE LOOP
# ==============================

while True:

    ret, img = cam.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    # Only capture first detected face (avoid multi-count)
    if len(faces) > 0:
        (x, y, w, h) = faces[0]

        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (100, 100))

        count += 1
        file_number = existing_images + count
        file_path = os.path.join(path, f"{file_number}.jpg")

        cv2.imwrite(file_path, face)

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.putText(
        img,
        f"Images: {count}/{max_images}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        img,
        "Press ESC to Exit",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    cv2.imshow("Face Capture", img)

    if cv2.waitKey(1) == 27 or count >= max_images:
        break

# ==============================
# CLEANUP
# ==============================

cam.release()
cv2.destroyAllWindows()

print("✅ Face Dataset Created Successfully!")
print(f"📁 Saved in: {path}")

# ==============================
# AUTO TRAIN AFTER CAPTURE
# ==============================

print("⚡ Starting Training Automatically...")
os.system("python train.py")
print("🎯 Training Completed!")