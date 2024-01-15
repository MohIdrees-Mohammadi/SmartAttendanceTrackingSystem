import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://viseion-based-attendence-sys-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')
data = {
    "203203651":
        {
            "name": "Mohammad Idrees",
            "major": "BSSE",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
"203203652":
        {
            "name": "Emily",
            "major": "BSSE",
            "starting_year": 2020,
            "total_attendance": 5,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
"203203653":
        {
            "name": "Naveed",
            "major": "BSSE",
            "starting_year": 2020,
            "total_attendance": 5,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

for key, value in data.items():
    ref.child(key).set(value)


