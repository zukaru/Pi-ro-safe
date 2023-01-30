import pyrebase as Firebase
import asyncio


config = {
        "apiKey": "AIzaSyBahiTuqQJcg9FJg1nexARrcAVi7lb_uZI",
        "authDomain": "pyrosafe-472f3.firebaseapp.com",
        "projectId": "pyrosafe-472f3",
        "storageBucket": "pyrosafe-472f3.appspot.com",
        "messagingSenderId": "930622732610",
        "appId": "1:930622732610:web:5cbb23878bb4c664c4b0db",
        "databaseURL": "https://pyrosafe-472f3-default-rtdb.firebaseio.com/",
        "serviceAccount":"firebase_private_credentials.json"
        }


class Db_service():

    

    def __init__(self) -> None:
        self.FSR = "FSR"

        self.FSSRList = []

        # Init firebase instance
        firebase = Firebase.initialize_app(config)

        # Init database service
        self.db = firebase.database()
        
        # Init storage bucket service
        self.sb = firebase.storage()

        # Init auth service
        self.auth = firebase.auth()


    # Will try signing in. If user is not found, will try creating an account.
    def authUser(self, email, pwd):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, pwd)
        except Exception as e:
            print(e)
            self.user = self.auth.create_user_with_email_and_password(email, pwd)

    
    def list_files_handler():
        pass
        
        

    # Get list of fire suppression system reports saved in storage bucket
    def getFSSRList(self):
        localReports = []
        reports = self.sb.list_files()
        for report in reports:
            print(report.public_url)
            localReports.append(report)
        return localReports.copy()
            




    def stream_handler(message):
        print(message["event"]) # put
        print(message["path"]) # /-K7yGTTEp7O549EzTYtI
        print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
        

    
    # No need to add reports from devices?
    # def addFSSRToList(self, FSSR):
    #     pass

    # def removeFSSRFromList(): 
    #     pass

