import pyrebase as Firebase
import kivy.uix.filechooser as FileChooser
import logic
import threading as th
import os

# Report naming convention
# mm-dd-yyyy
# Easily manage and sort relavent reports 


reports_dir = r"logs/sys_report"

schema = {
    "lights_on": False,
    "fans_on": False,
    "sys_report_list": [],
    "messages": []
}


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
        self.email = ""

        self.FSSRList = []

        # Init firebase instance
        firebase = Firebase.initialize_app(config)

        # Init database service
        self.db = firebase.database()
        
        # Init storage bucket service
        self.sb = firebase.storage()

        # Init auth service
        self.auth = firebase.auth()
        self.getUserEmail



    def authUser(self, email: str, password: str) -> None:
        '''Attempts to sign in.
        If user is not found, will try creating an account.
        '''
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            data = {"email": self.user["email"]}
            # self.db.child("users").push(data, self.user["idToken"])
            print(self.user)
            

        except Exception as e:
            # Assumption is that any exception is from email not being found
            # TODO Should check error message to confirm email is not found
            print(e)
            self.user = self.auth.create_user_with_email_and_password(email, password)
            
            
        finally:
            self.email = self.user["email"]
            self.path = "users/" + self.user["localId"]
            self.token = self.user["idToken"]
            self.uid = self.user["localId"]
            self.dbStream = self.db.child(self.path).stream(self.stream_handler,self.token)
            self.db.child(self.path).update({"email": self.email}, self.token)
            refresh_token = th.Timer(5, print,["testing"])
            refresh_token.start()
          


    def getUserEmail(self) -> str:
        if self.user["email"]:
            return self.user["email"]
        else:
            return "Email not found"

    def getCurrentUser(self):
        print(self.auth.current_user)


    def toggleLights(self, lights_on: int):
        data = {"lights_on": lights_on}
        self.db.child(self.path).update(data, self.token)



    

    def toggleFans(self, fans_on: int):
        data = {"fans_on": fans_on}
        self.db.child(self.path).update(data, self.token)
    


    def addReport(self):
        with open(reports_dir) as report:
            report.read()
        self.sb.child(self["user"]).put(report, self["user"])


    def getReport(self, file):
        self.sb.child(self["user"]).list_files()

    
    def delReport(self, name):
        self.sb.child(self["user"] + '/' + name).delete()
    

    # Get list of fire suppression system reports saved in storage bucket
    def getCloudReportList(self):
        unSyncedReports = []
        localReports = []
        cloudReports = []

        if len(cloudReports) == len(localReports):
            return
        
        elif len(cloudReports) > len(localReports):
            # do some type of
            pass
        reports = self.sb.list_files()
        for report in reports:
            print(report.name)
            
            # print(report.metadata)
            # print(report.public_url)
            # localReports.append(dir(report))
            
        return localReports.copy()



    def debounceFunc(self, cb, arg: list):
        try:
            self.light_deb
        except NameError:
            self.light_deb = th.Timer(2, cb, arg)  
            self.light_deb.start()
        else:
            self.light_deb.cancel()
            
        




    def stream_handler(self, message):
        print(message)
        print(message["event"]) # put
        print(message["path"]) # /-K7yGTTEp7O549EzTYtI
        print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}