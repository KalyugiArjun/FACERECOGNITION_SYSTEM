import cv2
import os
import sqlite3
from datetime import datetime

dataPath = 'dataset'
imagePaths = os.listdir(dataPath)

face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('trainer.yml')

cap = cv2.VideoCapture(0)

faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# MEMORY LOCK (Ek baar attendance hone ke baad dobara nahi hogi)
marked = []

def mark_attendance(name):

    if name not in marked:

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        # Same student same day check
        cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name,date))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO attendance(name,date,time) VALUES(?,?,?)", (name,date,time))
            conn.commit()
            print("Attendance Marked for", name)

            marked.append(name)   # Lock laga diya

        conn.close()

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceClassif.detectMultiScale(gray,1.3,5)

    for(x,y,w,h) in faces:

        rostro = gray[y:y+h,x:x+w]
        rostro = cv2.resize(rostro,(150,150),interpolation=cv2.INTER_CUBIC)

        result = face_recognizer.predict(rostro)

        if result[1] < 70:

            name = imagePaths[result[0]]
            cv2.putText(frame,name,(x,y-5),1,1.3,(0,255,0),2)

            if name not in marked:
                mark_attendance(name)

        else:
            cv2.putText(frame,'Unknown',(x,y-5),1,1.3,(0,0,255),2)

        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

    cv2.imshow('Face Recognition Attendance System',frame)

    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()