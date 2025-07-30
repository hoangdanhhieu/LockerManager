import requests
import json
from datetime import datetime

def tesgetUserimg():
    url = "http://127.0.0.1:8000/api/get_user_image/"
    data = {
        "passwd_lock_admin": "Hoanghieu.2702",
        "user_id": "1"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        with open("downloaded_image.jpg", "wb") as f:
            f.write(response.content)
    else:
        print(response.json())

def testUpload():
    url = "http://127.0.0.1:8000/api/upload_user_image/"
    data = {
        "passwd_lock_admin": "Hoanghieu.2702",
        "user_id": "1"
    }   
    files = {
        "image": open("/home/nonamezz/Downloads/cow.jpeg", "rb")
    }
    
    response = requests.post(url, data=data, files=files)
    print(response.json())


def send_vectorid():
    url = "http://127.0.0.1:8000/api/update_user_vector/"
    data = {
        "passwd_lock_admin": "Hoanghieu.2702",
        "user_id": 1,
        "vector": json.dumps([0.1, 0.2, 0.3, 0.4])  # or any JSON-serializable object
    }
    response = requests.post(url, data=data)
    print(response.json())

def get_vectorid():
    url = "http://127.0.0.1:8000/api/get_user_vector/"
    data = {
        "passwd_lock_admin": "Hoanghieu.113",
        "user_id": 1
    }
    response = requests.post(url, data=data)
    print(response.json())

def write_log():
    url = "http://127.0.0.1:8000/api/write_log/"
    data = {
        "passwd_lock_admin": "Hoanghieu.2702",
        "code": 4,
        "locker_id": 4,
        "board_id": 4,
        "details": "",
    }
    response = requests.post(url, data=data)
    print(response.json())

def get_user_list():
    url = "http://127.0.0.1:8000/api/get_user_list/"
    data = {"passwd_lock_admin": "Hoanghieu.2702"}
    response = requests.post(url, data=data)
    print(response.json())

def reg_user():
    url = "https://lockermanager.onrender.com/api/register_user"
    data = {"passwd_lock_admin": "Hoanghieu.2702", "name": "Anh Da Den", "sdt": "0368566777", "status": 1}
    response = requests.post(url, data=data)
    print(response.json())
reg_user()