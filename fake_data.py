import requests
import random
import base64
import os
from datetime import datetime, timedelta
import pytz
import uuid
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
BASE_URL = os.getenv("BASE_URL")

# 台灣時區
taiwan_tz = pytz.timezone('Asia/Taipei')

# 真實使用者資料列表
users = [
  {
    "UserID": "U81cd82f7e60a4bf88a100fc6e08e5a3f",
    "UserName": "peter",
    "UserPic": "https://sprofile.line-scdn.net/0hFwy7VNPyGVhUTg8uUL5nJyQeGjJ3P0BKfiBTNmceEj88ew1deyFSODVJEmE7LQlZK39VNzQbQm9YXW4-ShjlbFN-RGloeVwIfShUvA",
    "NickName": "葉禮嘉",
    "Role": "admin"
  },
  {
    "UserID": "U2034af6f969f80408c35190ad4edcc5a",
    "UserName": "均嘉工程-公務機（黃謝惟）",
    "UserPic": "https://sprofile.line-scdn.net/0hPG2gFgn3D2gfHh_aS81xF29ODAI8b1Z6M39EDiobAwpyKUlrMS9HCSkcAggrL0E5Y38VDXkWAV0TDXgOAUjzXBguUlkjKUo4NnhCjA",
    "NickName": "均嘉工程-公務機（黃謝惟）-均嘉工程",
    "Role": "admin"
  },
  {
    "UserID": "Ub2d28242b1ead101aee416e9043ad2e0",
    "UserName": "Hank_Lin",
    "UserPic": "https://sprofile.line-scdn.net/0h89rg4QokZxZfHnPskb8ZaS9OZHx8bz4EcCwgI2JLOiU1KSNGdXwuc2hOOCVifiREeioocW9Ka3VTDRBwQUibIlguOidjKSJGdngq8g",
    "NickName": "linebot開發人員測試",
    "Role": "admin"
  },
  {
    "UserID": "U5fb140529f80d9046ed157da4a4ef853",
    "UserName": "昀生",
    "UserPic": "https://sprofile.line-scdn.net/0hWYAWmA4ACHZsLiCH8o92CRx-CxxPX1FkSUwTGFkqBBFSShwpSBxPFgsoA04CGBh3EElOFlEvVxJgPX8Qcnj0QmseVUdQGU0mRUhFkg",
    "NickName": "陳昀生",
    "Role": "manager"
  },
  {
    "UserID": "U3f2f27167d4ea53d0d174abfc143c2ac",
    "UserName": "海狗",
    "UserPic": "https://sprofile.line-scdn.net/0hoINWjTBGMGZjLiCR6BtOGRN-MwxAX2l0HxsvAlN7aF8KGCIwTBgqAFcobF9aTiJnSUwsBwZ6b1VvPUcAfXjMUmQebVdfGXU2Skh9gg",
    "NickName": "戴奇海",
    "Role": "none"
  }
]

# 假案件資料
cases = [
  {
    "CaseID": "C001",
    "Name": "台北市信義區住宅新建工程",
    "GroupID": "G001",
    "Location": "台北市信義區松仁路100號",
    "Content": "15層住宅新建，含地下3層停車場",
    "Status": "進行中"
  },
  {
    "CaseID": "C002",
    "Name": "新北市板橋區辦公大樓整修工程",
    "GroupID": "G001",
    "Location": "新北市板橋區民生路50號",
    "Content": "8層辦公大樓外牆及內部整修",
    "Status": "進行中"
  },
  {
    "CaseID": "C003",
    "Name": "桃園市中壢區商場擴建工程",
    "GroupID": "G002",
    "Location": "桃園市中壢區中央西路二段120號",
    "Content": "既有商場擴建及內部裝修",
    "Status": "規劃中"
  }
]

# 生成假照片資料 (base64編碼的簡單圖像)
def generate_fake_photo():
  # 這裡只是生成一個簡單的1x1像素透明圖片的base64字串
  # 實際應用中可以使用真實照片
  return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# 生成隨機日期時間
def random_datetime(start_date, end_date=None, is_clock_in=True):
  if end_date is None:
    end_date = datetime.now(taiwan_tz)
  
  time_between_dates = end_date - start_date
  days_between_dates = time_between_dates.days
  random_number_of_days = random.randrange(days_between_dates)
  random_date = start_date + timedelta(days=random_number_of_days)
  
  if is_clock_in:
    # 上班時間 (7:00 - 9:00之間)
    hour = random.randint(7, 9)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
  else:
    # 下班時間 (16:00 - 19:00之間)
    hour = random.randint(16, 19)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
  
  return random_date.replace(hour=hour, minute=minute, second=second)

# 生成打卡資料
def generate_attendance_data(num_records=50):
  attendance_records = []
  
  # 設定起始日期為30天前
  start_date = datetime.now(taiwan_tz) - timedelta(days=30)
  
  # 為每個使用者生成打卡記錄
  for user in users:
    # 為每個使用者生成幾筆記錄
    user_records = int(num_records / len(users)) + (1 if random.random() > 0.5 else 0)
    
    for _ in range(user_records):
      # 選擇隨機案件
      case = random.choice(cases)
      
      # 生成上班時間
      clock_in_time = random_datetime(start_date, is_clock_in=True)
      
      # 根據角色調整工作時間
      if user["Role"] == "admin":
        # 管理員工作時間較長 (8-10小時)
        work_hours = random.randint(8, 10)
      elif user["Role"] == "manager":
        # 經理工作時間中等 (7-9小時)
        work_hours = random.randint(7, 9)
      else:
        # 一般員工工作時間 (6-8小時)
        work_hours = random.randint(6, 8)
      
      # 生成下班時間
      clock_out_time = random_datetime(clock_in_time.replace(hour=0, minute=0, second=0), 
                                     clock_in_time.replace(hour=23, minute=59, second=59), 
                                     is_clock_in=False)
      
      # 確保下班時間在上班時間之後
      while clock_out_time <= clock_in_time:
        clock_out_time = clock_in_time + timedelta(hours=work_hours)
      
      # 生成打卡記錄
      record = {
        "AttendanceID": str(uuid.uuid4()),
        "UserID": user["UserID"],
        "UserName": user["UserName"],
        "CaseID": case["CaseID"],
        "CaseName": case["Name"],
        "ClockInTime": clock_in_time.isoformat(),
        "ClockOutTime": clock_out_time.isoformat(),
        "ClockInPhoto": generate_fake_photo(),
        "ClockOutPhoto": generate_fake_photo(),
        "IsTrained": True,
        "WorkHours": (clock_out_time - clock_in_time).total_seconds() / 3600
      }
      
      attendance_records.append(record)
  
  return attendance_records

# 發送打卡資料到API
def post_attendance_data(records):
  success_count = 0
  error_count = 0
  
  for record in records:
    try:
      # 先發送上班打卡
      clock_in_data = {
        "CaseID": record["CaseID"],
        "UserID": record["UserID"],
        "IsTrained": record["IsTrained"],
        "ClockInPhoto": record["ClockInPhoto"]
      }
      
      # 發送上班打卡請求
      clock_in_response = requests.post(f"{BASE_URL}/attendance/clock-in", json=clock_in_data)
      clock_in_response.raise_for_status()
      
      # 獲取打卡ID
      attendance_id = clock_in_response.json()["AttendanceID"]
      
      # 發送下班打卡
      clock_out_data = {
        "ClockOutPhoto": record["ClockOutPhoto"]
      }
      
      # 發送下班打卡請求
      clock_out_response = requests.post(f"{BASE_URL}/attendance/{attendance_id}/clock-out", json=clock_out_data)
      clock_out_response.raise_for_status()
      
      success_count += 1
      print(f"成功建立打卡記錄 {success_count}/{len(records)}: {record['UserName']} 在 {record['CaseName']}")
      
    except Exception as e:
      error_count += 1
      print(f"建立打卡記錄失敗: {str(e)}")
  
  print(f"完成! 成功: {success_count}, 失敗: {error_count}")

# 創建使用者資料
def create_fake_users():
  success_count = 0
  error_count = 0
  
  for user in users:
    try:
      response = requests.post(f"{BASE_URL}/users", json=user)
      response.raise_for_status()
      success_count += 1
      print(f"成功建立使用者: {user['UserName']}")
    except requests.exceptions.HTTPError as e:
      if e.response.status_code == 409:
        print(f"使用者已存在: {user['UserName']}")
        success_count += 1
      else:
        error_count += 1
        print(f"建立使用者失敗 {user['UserName']}: {str(e)}")
    except Exception as e:
      error_count += 1
      print(f"建立使用者失敗 {user['UserName']}: {str(e)}")
  
  print(f"使用者建立完成! 成功: {success_count}, 失敗: {error_count}")

# 創建案件資料
def create_fake_cases():
  success_count = 0
  error_count = 0
  
  for case in cases:
    try:
      # 檢查案件是否已存在
      try:
        check_response = requests.get(f"{BASE_URL}/cases/{case['CaseID']}")
        if check_response.status_code == 200:
          print(f"案件已存在: {case['Name']}")
          success_count += 1
          continue
      except:
        pass
      
      # 建立案件
      response = requests.post(f"{BASE_URL}/cases", json={
        "Name": case["Name"],
        "GroupID": case["GroupID"],
        "Location": case["Location"],
        "Content": case["Content"]
      })
      response.raise_for_status()
      success_count += 1
      print(f"成功建立案件: {case['Name']}")
    except Exception as e:
      error_count += 1
      print(f"建立案件失敗 {case['Name']}: {str(e)}")
  
  print(f"案件建立完成! 成功: {success_count}, 失敗: {error_count}")

# 主函數
def main():
  print("開始建立假資料...")
  
  # 建立使用者
  create_fake_users()
  
  # 建立案件
  create_fake_cases()
  
  # 生成打卡資料
  print("生成打卡資料...")
  attendance_records = generate_attendance_data(30)  # 生成約30筆打卡記錄
  
  # 發送打卡資料
  print("發送打卡資料到API...")
  post_attendance_data(attendance_records)
  
  print("假資料建立完成!")
  
  # 顯示生成的資料摘要
  user_summary = {}
  for record in attendance_records:
    user_id = record["UserID"]
    user_name = record["UserName"]
    if user_id not in user_summary:
      user_summary[user_id] = {
        "name": user_name,
        "count": 0,
        "total_hours": 0
      }
    
    user_summary[user_id]["count"] += 1
    user_summary[user_id]["total_hours"] += record["WorkHours"]
  
  print("\n生成的打卡資料摘要:")
  for user_id, data in user_summary.items():
    print(f"{data['name']} - {data['count']} 筆打卡記錄，總工時: {data['total_hours']:.2f} 小時")

if __name__ == "__main__":
  main()
