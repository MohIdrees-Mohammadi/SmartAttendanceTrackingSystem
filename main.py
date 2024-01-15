import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://viseion-based-attendence-sys-default-rtdb.firebaseio.com/",
    'storageBucket': "viseion-based-attendence-sys.appspot.com"
})
bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resourses/background.png')

# taking modes and converting to array form
modePath = 'Resourses/mode'
modePathList = os.listdir(modePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(modePath, path)))

# Screen Resizing options
# cv2.namedWindow('Smart_Attendance_System', cv2.WINDOW_NORMAL)  # Create a resizable window
# cv2.setWindowProperty('Smart_Attendance_System', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # Make it non-resizable


# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    # Scalling down the image not the pixcel of image
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # targetting the face from image and comparing it with known faces
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[196:196 + 480, 60:60 + 640] = img
    imgBackground[85:85+580, 806:806+423] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                # print('Known face has been detected')
                # print('studentId', studentIds[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 60+x1, 196+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0, colorC=(255,0,120))
                id = studentIds[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 3
            else:
                modeType = 4
                imgBackground[85:85 + 580, 806:806 + 423] = imgModeList[modeType]

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # downloading student image
                blob = bucket.get_blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modeType = 2
                    counter = 0
                    imgBackground[85:85+580, 806:806+423] = imgModeList[modeType]

            if modeType != 2:
                if 10<counter<20:
                    imgBackground[85:85 + 580, 806:806 + 423] = imgModeList[1]

                if counter <= 10:
                    imgBackground[68:68 + 367, 815:815 + 406] = imgStudent
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']),(1178, 410), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255),2)

                    # aligning the Name to the center of the image
                    (w,h),_ =cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (423-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (806+offset, 460), cv2.FONT_HERSHEY_COMPLEX, 1,(255, 255, 255), 1)


                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[85:85+580, 806:806+423] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
        secondsElapsed = 0

    cv2.imshow('Smart_Attendance_System', imgBackground)
    cv2.waitKey(1)


