import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def create_user(user_id: str, user_name: str, user_pic: str, nick_name: str):
    user_data = {
        "UserID": user_id,
        "UserName": user_name,
        "UserPic": user_pic,
        "NickName": nick_name
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    response.raise_for_status()
    return response.json()

def get_users(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/users")
    response.raise_for_status()
    return response.json()

def get_user(user_id: str):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    # return status code and json data
    if response.status_code == 404:
        return None
    else:
        response.raise_for_status()
        return response.json()

def update_user_role(user_id: str, role: str):
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role", json={"Role": role})
    response.raise_for_status()
    return response.json()

def get_groups(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/groups")
    response.raise_for_status()
    return response.json()

def get_cases(skip: int = 0, limit: int = 100):
    response = requests.get(f"{BASE_URL}/cases")
    response.raise_for_status()
    return response.json()

def get_case_by_id(case_id: str):
    response = requests.get(f"{BASE_URL}/cases/{case_id}")
    response.raise_for_status()
    return response.json()

def get_photos():
    response = requests.get(f"{BASE_URL}/photos/query")
    response.raise_for_status()
    return response.json()

def get_photo_by_id(photo_id: str):
    response = requests.get(f"{BASE_URL}/photos/{photo_id}")
    response.raise_for_status()
    return response.json()

def patch_photo_status_and_caseid(photo_id: str, status: str, case_id: str):

    photo_json_data = {
        "Status": status,
        "CaseID": case_id
    }

    # 使用 requests 進行 PATCH 請求，並將資料轉換為 JSON
    response = requests.patch(f"{BASE_URL}/photos/{photo_id}/", json=photo_json_data)
    response.raise_for_status()  # 如果請求失敗，會觸發異常

    return response.json()  # 返回伺服器回應的 JSON 資料

def patch_photo_phase(photo_id: str,status:str, phase: str):

    photo_json_data = {
        "Status": status,
        "Phase": phase
    }

    # 使用 requests 進行 PATCH 請求，並將資料轉換為 JSON
    response = requests.patch(f"{BASE_URL}/photos/{photo_id}/", json=photo_json_data)
    response.raise_for_status()  # 如果請求失敗，會觸發異常

    return response.json()  # 返回伺服器回應的 JSON 資料
