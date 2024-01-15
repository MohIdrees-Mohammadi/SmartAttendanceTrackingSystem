import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://viseion-based-attendence-sys-default-rtdb.firebaseio.com/",
    'storageBucket': "viseion-based-attendence-sys.appspot.com"
})


folderPath = 'images'
studentPathList = os.listdir(folderPath)
studentIds = []
imgList = []
for path in studentPathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
#   uploading photo to database
    fileName = f'{folderPath}/{path}'
    storage.bucket().blob(fileName).upload_from_filename(fileName)


# image ecoding function
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnownWithIds)
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
