import requests
import json

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
        "passwd_lock_admin": "Hoanghieu.2702",
        "user_id": 1
    }
    response = requests.post(url, data=data)
    print(response.json())

def write_log():
    url = "http://127.0.0.1:8000/api/write_log/"
    data = {
        "passwd_lock_admin": "Hoanghieu.2702",
        "code": 0,
        "details": "Mở khóa tủ #2",
    }
    response = requests.post(url, data=data)
    print(response.json())
write_log()