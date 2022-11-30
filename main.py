from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager ,Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.pickers import MDDatePicker,MDTimePicker
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDIconButton
import pymongo
import threading
import time
import datetime
from datetime import date 
from datetime import datetime
from bson.objectid import ObjectId
import time
import plyer
from kivy.properties import  StringProperty,ObjectProperty
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
Window.size =(320,580)
import socket
import threading

import port as port

HOST = socket.gethostbyname(socket.gethostname())  # dynamically assigns the addr
PORT = 2426

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(HOST, port)

server.listen()

clients = []
nicknames = []

client = pymongo.MongoClient("mongodb+srv://mindbridge:root@cluster0.rf18f.mongodb.net/test")
db = client['reminder']
collection = db['users']


class TodoCard(CommonElevationBehavior,MDFloatLayout):
    label = StringProperty('')
    date = StringProperty('')
    time = StringProperty('')
    _id = StringProperty('')

class user:
    name = None
    task = []
    
    def load_task(self):
        collection = db['tasks']
        data = collection.find({"creator":self.name})
        for i in data:
            self.task.append({"id":i['_id'],"creator":self.name,"date": i['date'],"time": i['time'],"name": i['name']})
    def setname(self,name):
        self.name = name 
    def setdata(self,date='2000-10-20',time='00:00:00',taskName= 'Task'):
            collection = db['tasks']
            p = collection.insert_one({"creator":self.name,"date": date,"time": time,"name": taskName})
            self.task.append({"id":str(p.inserted_id),"creator":self.name,"date": date,"time": time,"name": taskName})
    
            
class login(MDApp):
    dialog= None
    data = user()
    def list_task(self):
            for p in screen_manager.get_screen('welcome').ids.todo_list.children:
                screen_manager.get_screen('welcome').ids.todo_list.remove_widget(p)
            for i in self.data.task:
                screen_manager.get_screen('welcome').ids.todo_list.add_widget(TodoCard(label=i['name'],date=i['date'],time=i['time'],_id=str(i['id'])))

    def checker(self):
        while(1):
            datetime = date.today()
            t = time.localtime()
            current_time = time.strftime("%H:%M", t)
            current = datetime.strftime("%Y-%m-%d")
            collection = db['tasks']
            data = collection.find({"creator":self.data.name})
            for i in data :
                tt= i['time']
                if(current==i['date'] and current_time==tt[0:5]):
                    plyer.notification.notify(title=f"{i['name']}",message="Tap to remove")
                    collection.delete_one({"_id" : i['_id']})
                    for p in range(0,len(self.data.task)):
                        print(self.data.task[p]['id'],i['_id'])
                        if(str(self.data.task[p]['id'])==str(i['_id']) ):
                            self.data.task.pop(p)
                            break
            time.sleep(10)

    def refresh(self):
        print(self.data.task)
        self.list_task()
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("login.kv"))
        screen_manager.add_widget(Builder.load_file("signup.kv"))
        screen_manager.add_widget(Builder.load_file("welcome.kv"))
        screen_manager.add_widget(Builder.load_file("task.kv"))
        screen_manager.add_widget(Builder.load_file("androidChat.kv"))

        return screen_manager
    def logout(self):
        screen_manager.get_screen("login").ids.email_login.text = ""
        screen_manager.get_screen("login").ids.pass_login.text =""
        screen_manager.transition.direction = "right"
        screen_manager.current= "login"
        self.data.name = None
        self.data.task = []

    def deleteData(self,instance):
        collection = db['tasks']
        collection.delete_one({"_id":ObjectId(instance.parent.ids['root._id'].text)})
        for i in range(0,len(self.data.task)):
            if(self.data.task[i]['id']==instance.parent.ids['root._id'].text ):
                self.data.task.pop(i)
                break
        self.list_task()
            

    def get_id(self,  instance):
        for id, widget in instance.parent.ids.items():
            if widget.__self__ == instance:
                return id

    def Login(self):
        email = screen_manager.get_screen("login").ids.email_login.text
        pass1 = screen_manager.get_screen("login").ids.pass_login.text
        if(email != "" and pass1!=""):
            p = collection.count_documents({"username": email , "password" : pass1})
            if(p>0):
                self.data.setname(email)
                self.data.load_task()
                screen_manager.get_screen("login").ids.email_login.text = ""
                screen_manager.get_screen("login").ids.pass_login.text = ""
                screen_manager.get_screen("login").ids.login_lable.text = ""
                screen_manager.transition.direction = "left"
                screen_manager.current= "welcome"
                name =self.data.name
                if(len(self.data.name)>7):
                    name = self.data.name[0:7] + "..."
                screen_manager.get_screen("welcome").ids.name_label.text = name
                t1 = threading.Thread(target=self.checker)
                t1.setDaemon(True)
                self.list_task()
                t1.start()              
                
            else:
                screen_manager.get_screen("login").ids.login_lable.text = "Account Not Found"
    def TaskButton(self):
        datetime = date.today()
        t = time.localtime()
        current_time = time.strftime("%H:%M", t)
        current_date = datetime.strftime("%Y-%m-%d")
        screen_manager.get_screen("task").ids.task_date_lable.text = current_date
        screen_manager.get_screen("task").ids.task_time_lable.text = current_time[0:5]
        screen_manager.get_screen("task").ids.task_name.text = ""
        self.list_task()
        screen_manager.transition.direction = "left"
        screen_manager.current = "task"
    def on_save_date(self,instance,value,date_range):
        screen_manager.get_screen("task").ids.task_date_lable.text = str(value)
    def on_cancel_date(self,instance,value):
        pass
    
    def get_time(self,instance,value):
        screen_manager.get_screen("task").ids.task_time_lable.text = str(value)[0:5]

    def Dpick(self): #pick date
        datetime = date.today()
        current_date = datetime.strftime("%Y-%m-%d").split('-')
        print(current_date)
        date_box = MDDatePicker(year=int(current_date[0]),month=int(current_date[1]) ,day=int(current_date[2]))
        date_box.bind(on_save=self.on_save_date,on_cancel=self.on_cancel_date)
        date_box.open()
    def Timepick(self):
        default = datetime.strptime("4:20:00",'%H:%M:%S').time()
        time_box = MDTimePicker()
        time_box.set_time(default)
        time_box.bind(on_cancel = self.on_cancel_date , time=self.get_time)
        time_box.open()
    def Addtask(self):
        name = screen_manager.get_screen("task").ids.task_name.text
        date = screen_manager.get_screen("task").ids.task_date_lable.text 
        time1 = screen_manager.get_screen("task").ids.task_time_lable.text
        if(name == ""):
            name= "no name"
        self.data.setdata(date,time1,name)
        self.list_task()
        screen_manager.transition.direction = "right"
        screen_manager.current = "welcome"
        
    def Signup(self):
        screen_manager.get_screen("signup").ids.email_create.disabled = False
        screen_manager.get_screen("signup").ids.pass_create.disabled = False
        screen_manager.get_screen("signup").ids.confirm_pass_create.disabled = False
        screen_manager.get_screen("signup").ids.email_create.text = ""
        screen_manager.get_screen("signup").ids.pass_create.text = ""
        screen_manager.get_screen("signup").ids.confirm_pass_create.text = ""
        screen_manager.get_screen("signup").ids.create_button.disabled = False
        screen_manager.get_screen("signup").ids.create_lable.text = ""
        screen_manager.get_screen("signup").ids.back_button.disabled = False
        screen_manager.transition.direction = "left"
        screen_manager.current = "signup"
    def AccountCreate(self):
        email = screen_manager.get_screen("signup").ids.email_create.text
        pass1 = screen_manager.get_screen("signup").ids.pass_create.text
        pass2 = screen_manager.get_screen("signup").ids.confirm_pass_create.text
        screen_manager.get_screen("signup").ids.email_create.disabled = True
        screen_manager.get_screen("signup").ids.pass_create.disabled = True
        screen_manager.get_screen("signup").ids.confirm_pass_create.disabled = True
        screen_manager.get_screen("signup").ids.create_button.disabled = True
        screen_manager.get_screen("signup").ids.back_button.disabled = True
        screen_manager.get_screen("signup").ids.create_lable.text = "Creating Account..."
        if(email!='' and pass1!='' and pass2!='' and pass1 == pass2):
            # checker = collection.find({"username" : email})
            if(collection.count_documents({"username":email})):
                screen_manager.get_screen("signup").ids.create_lable.text = "Account Already Exist"
                screen_manager.get_screen("signup").ids.email_create.disabled = False
                screen_manager.get_screen("signup").ids.pass_create.disabled = False
                screen_manager.get_screen("signup").ids.confirm_pass_create.disabled = False
                screen_manager.get_screen("signup").ids.create_button.disabled = False
                screen_manager.get_screen("signup").ids.back_button.disabled = False
            # collection.insert_one({"username" : "talha","password" : "123"})
            elif(collection.insert_one({"username" : email,"password" : pass1})):
                screen_manager.get_screen("signup").ids.create_lable.text = "Creating Created Succesfully"
                screen_manager.transition.direction = "left"
                screen_manager.current = "login"
            else:
                screen_manager.get_screen("signup").ids.create_lable.text = "Account Failed to Create"
                screen_manager.get_screen("signup").ids.email_create.disabled = False
                screen_manager.get_screen("signup").ids.pass_create.disabled = False
                screen_manager.get_screen("signup").ids.confirm_pass_create.disabled = False
                screen_manager.get_screen("signup").ids.create_button.disabled = False
                screen_manager.get_screen("signup").ids.back_button.disabled = False
        else:
            screen_manager.get_screen("signup").ids.create_lable.text = "Email and Password Required"
            screen_manager.get_screen("signup").ids.email_create.disabled = False
            screen_manager.get_screen("signup").ids.pass_create.disabled = False
            screen_manager.get_screen("signup").ids.confirm_pass_create.disabled = False
            screen_manager.get_screen("signup").ids.create_button.disabled = False
            screen_manager.get_screen("signup").ids.back_button.disabled = False
    
    def broadcast(message):
    for client in clients:
        client.send(message)

def handle_connection(client):
    stop = False
    while not stop:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} left the chat.".encode('utf-8'),
                      stop = True)
def main():
    print("Server is working....")
    while True:
        client, addr = server.accept()
        print(f"Connected to {addr}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        clients.append(client)
        print(f"Nickname is {nickname}")

        broadcast(f"{nickname} joined the chat.")

        client.send("You are now connected.".encode('utf-8'))

        thread = threading.Thread(target=handle_connection(client,))
        thread.start()

login().run()
# t1.join()
