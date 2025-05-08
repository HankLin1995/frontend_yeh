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

def create_case(case_name: str, group_id: str, location: str, content: str):
    case_data = {
        "Name": case_name,
        "GroupID": group_id,
        "Location": location,
        "Content": content
    }
    response = requests.post(f"{BASE_URL}/cases", json=case_data)
    response.raise_for_status()
    return response.json()

def get_case_by_id(case_id: str):
    response = requests.get(f"{BASE_URL}/cases/{case_id}")
    response.raise_for_status()
    return response.json()

def update_case(case_id: str, case_name: str, location: str, content: str, status: str):
    case_data = {
        "Name": case_name,
        "Location": location,
        "Content": content,
        "Status": status
    }
    response = requests.patch(f"{BASE_URL}/cases/{case_id}", json=case_data)
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


#### 員工、薪資、證照

def get_users():

    resp = requests.get(f"{BASE_URL}/users")
    resp.raise_for_status()
    return resp.json()

def get_employees():

    resp = requests.get(f"{BASE_URL}/employees")
    resp.raise_for_status()
    return resp.json()

def create_employee(data):

    resp = requests.post(f"{BASE_URL}/employees", json=data)
    resp.raise_for_status()
    return resp.json()

def update_employee(employee_id, data):

    resp = requests.patch(f"{BASE_URL}/employees/{employee_id}", json=data)
    resp.raise_for_status()
    return resp.json()

def delete_employee(employee_id):

    resp = requests.delete(f"{BASE_URL}/employees/{employee_id}")
    resp.raise_for_status()
    return resp.json()

def get_employee_detail(line_id):

    resp = requests.get(f"{BASE_URL}/employees/{line_id}")
    # resp.raise_for_status()
    return resp.json()

# 證照

def get_certificates(employee_id):

    resp = requests.get(f"{BASE_URL}/employees/{employee_id}/certificates")
    resp.raise_for_status()
    return resp.json()

def create_certificate(data):

    resp = requests.post(f"{BASE_URL}/employees/certificates/", json=data)
    resp.raise_for_status()
    return resp.json()

def upload_certificate_file(employee_id, file, certificate_name, issue_date=None, expiry_date=None):
    """
    上傳證照檔案，並建立 Certificate 資料
    Args:
        employee_id: 員工ID
        file: 證照檔案 (二進位)
        certificate_name: 證照名稱
        issue_date: 發證日 (可選)
        expiry_date: 到期日 (可選)
    """
    url = f"{BASE_URL}/employees/{employee_id}/certificates/upload"
    files = {"file": file}
    data = {"certificate_name": certificate_name}
    if issue_date:
        data["issue_date"] = issue_date
    if expiry_date:
        data["expiry_date"] = expiry_date
    resp = requests.post(url, files=files, data=data)
    resp.raise_for_status()
    return resp.json()

def update_certificate(certificate_id, data):

    resp = requests.patch(f"{BASE_URL}/employees/certificates/{certificate_id}", json=data)
    resp.raise_for_status()
    return resp.json()

def delete_certificate(certificate_id):

    resp = requests.delete(f"{BASE_URL}/employees/certificates/{certificate_id}")
    resp.raise_for_status()
    return resp.json()

# ====== 材料管理 ======

def get_materials(skip=0, limit=1000, name=None, unit=None):
    params = {"skip": skip, "limit": limit}
    if name:
        params["name"] = name
    if unit:
        params["unit"] = unit
    resp = requests.get(f"{BASE_URL}/materials/", params=params)
    resp.raise_for_status()
    return resp.json()

# return status
def create_material(data):
    resp = requests.post(f"{BASE_URL}/materials/", json=data)
    # resp.raise_for_status()
    return resp.json()

def update_material(material_id, data):
    resp = requests.put(f"{BASE_URL}/materials/{material_id}", json=data)
    resp.raise_for_status()
    return resp.json()

def delete_material(material_id):
    resp = requests.delete(f"{BASE_URL}/materials/{material_id}")
    resp.raise_for_status()
    return resp.json()

# ====== 設備管理 ======

def get_equipments(skip=0, limit=1000, name=None, status=None):
    params = {"skip": skip, "limit": limit}
    if name:
        params["name"] = name
    if status:
        params["status"] = status
    resp = requests.get(f"{BASE_URL}/equipments/", params=params)
    resp.raise_for_status()
    return resp.json()

def get_equipment_detail(equipment_id):
    resp = requests.get(f"{BASE_URL}/equipments/{equipment_id}")
    resp.raise_for_status()
    return resp.json()

def create_equipment(data):
    resp = requests.post(f"{BASE_URL}/equipments/", json=data)
    # resp.raise_for_status()
    return resp.json()

def update_equipment(equipment_id, data):
    resp = requests.put(f"{BASE_URL}/equipments/{equipment_id}", json=data)
    resp.raise_for_status()
    return resp.json()

def delete_equipment(equipment_id):
    resp = requests.delete(f"{BASE_URL}/equipments/{equipment_id}")
    resp.raise_for_status()
    return resp.json()

# 借用紀錄

def create_equipment_borrow_log(data):
    resp = requests.post(f"{BASE_URL}/equipments/borrow", json=data)
    resp.raise_for_status()
    return resp.json()

def get_equipment_borrow_log(log_id):
    resp = requests.get(f"{BASE_URL}/equipments/borrow/{log_id}")
    resp.raise_for_status()
    return resp.json()

def get_equipment_borrow_logs(equipment_id, skip=0, limit=100):
    params = {"skip": skip, "limit": limit}
    resp = requests.get(f"{BASE_URL}/equipments/{equipment_id}/borrow_logs", params=params)
    resp.raise_for_status()
    return resp.json()

# 薪資

def get_salaries(employee_id):
    resp = requests.get(f"{BASE_URL}/employees/{employee_id}/salaries")
    resp.raise_for_status()
    return resp.json()

def create_salary(data):
    resp = requests.post(f"{BASE_URL}/employees/salaries/", json=data)
    resp.raise_for_status()
    return resp.json()

def delete_salary(salary_id):
    
    resp = requests.delete(f"{BASE_URL}/employees/salaries/{salary_id}")
    resp.raise_for_status()
    return resp.json()

# ====== 打卡 ======

def create_clock_in(data):
    resp = requests.post(f"{BASE_URL}/attendance/clock-in", json=data)
    resp.raise_for_status()
    return resp.json()

def create_clock_out(attendance_id,data):
    resp = requests.post(f"{BASE_URL}/attendance/{attendance_id}/clock-out", json=data)
    resp.raise_for_status()
    return resp.json()

def get_attendance_by_user_id(user_id):
    resp = requests.get(f"{BASE_URL}/attendance/query?UserID={user_id}")
    resp.raise_for_status()
    return resp.json()