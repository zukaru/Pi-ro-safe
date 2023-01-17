from firebase import Firebase



class Db_service():

    

    def __init__(self) -> None:

        config = {
        "apiKey": "AIzaSyBahiTuqQJcg9FJg1nexARrcAVi7lb_uZI",
        "authDomain": "pyrosafe-472f3.firebaseapp.com",
        "projectId": "pyrosafe-472f3",
        "storageBucket": "pyrosafe-472f3.appspot.com",
        "messagingSenderId": "930622732610",
        "appId": "1:930622732610:web:5cbb23878bb4c664c4b0db",
        "databaseURL": "https://pyrosafe-472f3-default-rtdb.firebaseio.com/"
        }
        firebase = Firebase(config)


        db = firebase.database()

        # data to save
        data = {
            "names": [
                "Caleb",
                "Zeb",
                "Cole"
            ]
        }

        # Pass the user's idToken to the push method
        results = db.child("users").push(data)


