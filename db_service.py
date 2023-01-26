import pyrebase as Firebase
import asyncio


config = {
        "apiKey": "AIzaSyBahiTuqQJcg9FJg1nexARrcAVi7lb_uZI",
        "authDomain": "pyrosafe-472f3.firebaseapp.com",
        "projectId": "pyrosafe-472f3",
        "storageBucket": "pyrosafe-472f3.appspot.com",
        "messagingSenderId": "930622732610",
        "appId": "1:930622732610:web:5cbb23878bb4c664c4b0db",
        "databaseURL": "https://pyrosafe-472f3-default-rtdb.firebaseio.com/"
        }


class Db_service():

    

    def __init__(self) -> None:
        self.FSR = "FSR"

        # Init firebase instance
        firebase = Firebase.initialize_app(config)

        # Init database service
        self.db = firebase.database()
        
        # Init storage bucket service
        self.sb = firebase.storage()

        # Init auth service
        self.auth = firebase.auth()


    # Will try signing in. If user is not found, will try creating an account.
    def authenticateUser(self, email, pwd):
        res = self.auth.create_user_with_email_and_password(email, pwd)
        print(res)
        

    def signUp(self, email, pwd):
        res = self.auth.create_user_with_email_and_password(email, pwd)
        print(res.error.message)
        

    # Get list of fire suppression system reports saved in storage bucket
    def getFSSRList(self):
         self.sb.list_files()

    
    # No need to add reports from devices?
    # def addFSSRToList(self, FSSR):
    #     pass

    # def removeFSSRFromList(): 
    #     pass

