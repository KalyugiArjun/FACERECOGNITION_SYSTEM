import cv2
import os
import numpy as np

dataPath = 'dataset'

# Faster LBPH Settings
recognizer = cv2.face.LBPHFaceRecognizer_create(
    radius=1,
    neighbors=8,
    grid_x=6,
    grid_y=6
)

faces = []
ids = []
label_map = {}
current_id = 0

print("⚡ Fast Training Started...")

for person_name in os.listdir(dataPath):

    person_path = os.path.join(dataPath, person_name)

    if not os.path.isdir(person_path):
        continue

    label_map[current_id] = person_name

    for image_name in os.listdir(person_path):

        image_path = os.path.join(person_path, image_name)

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        # Resize for speed (very important)
        img = cv2.resize(img, (100,100))

        faces.append(img)
        ids.append(current_id)

    current_id += 1


if len(faces) == 0:
    print("❌ No faces found in dataset")
    exit()

recognizer.train(faces, np.array(ids))

if not os.path.exists("trainer"):
    os.makedirs("trainer")

recognizer.save('trainer/trainer.yml')

print("✅ Training Completed FAST!")