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
    "Name": "A8外牆油漆案",
    "GroupID": "C62c6453716f2fea956ed598cba252cf8",
    "Location": "A8",
    "Content": "油漆、壁癌處理",
    "CaseID": 1,
    "CreateTime": "2024-11-13T21:31:38.467836",
    "Status": "new"
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
def generate_attendance_data(num_records=50, date_range_days=30, case_list=None):
  attendance_records = []
  
  # 如果沒有提供案件列表，使用預設案件
  if case_list is None:
    case_list = cases
  
  # 確保至少有一個案件
  if not case_list:
    print("錯誤：沒有可用的案件資料")
    return []
  
  # 設定起始日期
  end_date = datetime.now(taiwan_tz)
  start_date = end_date - timedelta(days=date_range_days)
  
  # 為每個使用者生成打卡記錄
  for user in users:
    # 為每個使用者生成幾筆記錄
    user_records = int(num_records / len(users)) + (1 if random.random() > 0.5 else 0)
    
    # 為使用者生成日期列表（不重複）
    user_dates = []
    for _ in range(user_records * 2):  # 生成足夠多的日期，以便篩選
      random_date = start_date + timedelta(days=random.randint(0, date_range_days))
      user_dates.append(random_date.replace(hour=0, minute=0, second=0, microsecond=0))
    
    # 去除重複日期並限制數量
    user_dates = list(set(user_dates))[:user_records]
    
    for work_date in user_dates:
      # 依據日期選擇案件（讓相同日期的使用者更可能在同一個案件）
      # 使用日期的數值作為隨機種子，使相同日期有較高機率選到同一個案件
      date_seed = work_date.day + work_date.month * 31
      random.seed(date_seed)
      case_weights = [random.random() * 10 for _ in range(len(case_list))]
      random.seed()  # 重置隨機種子
      
      # 根據權重選擇案件
      total_weight = sum(case_weights)
      case_probs = [w / total_weight for w in case_weights]
      case_index = random.choices(range(len(case_list)), weights=case_probs, k=1)[0]
      case = case_list[case_index]
      
      # 生成上班時間（在工作日的早上）
      clock_in_hour = random.randint(7, 9)
      clock_in_minute = random.randint(0, 59)
      clock_in_time = work_date.replace(hour=clock_in_hour, minute=clock_in_minute)
      
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
      clock_out_time = clock_in_time + timedelta(hours=work_hours)
      # 加入一些隨機變化
      clock_out_time += timedelta(minutes=random.randint(-30, 30))
      
      # 確保下班時間在上班時間之後且在合理範圍內
      while clock_out_time <= clock_in_time:
        clock_out_time = clock_in_time + timedelta(hours=work_hours)
      
      # 計算實際工作時間（小時）
      work_hours_actual = (clock_out_time - clock_in_time).total_seconds() / 3600
      
      # 生成打卡記錄
      record = {
        "AttendanceID": str(uuid.uuid4()),
        "UserID": user["UserID"],
        "UserName": user["UserName"],
        "CaseID": int(case["CaseID"].replace("C", "")) if isinstance(case["CaseID"], str) else case["CaseID"],
        "CaseName": case["Name"],
        "ClockInTime": clock_in_time,
        "ClockOutTime": clock_out_time,
        "ClockInPhoto": generate_fake_photo(),
        "ClockOutPhoto": generate_fake_photo(),
        "IsTrained": random.random() > 0.1,  # 90% 的機率為已受訓
        "WorkHours": round(work_hours_actual, 2)
      }
      
      attendance_records.append(record)
  
  # 按日期排序
  attendance_records.sort(key=lambda x: x["ClockInTime"])
  
  return attendance_records

# 發送打卡資料到API
def post_attendance_data(records):
  success_count = 0
  error_count = 0
  
  for i, record in enumerate(records):
    try:
      # 先發送上班打卡
      clock_in_data = {
        "CaseID": record["CaseID"],
        "UserID": record["UserID"],
        "IsTrained": True,
        "ClockInPhoto": record["ClockInPhoto"]
      }
      
      # 發送上班打卡請求
      clock_in_response = requests.post(f"{BASE_URL}/attendance/clock-in", json=clock_in_data)
      clock_in_response.raise_for_status()

      print(clock_in_response.json())
      
      # 獲取打卡ID
      attendance_id = clock_in_response.json()["AttendanceID"]
      
      # 發送下班打卡
      clock_out_data = {
        "ClockOutPhoto": record["ClockOutPhoto"]
      }
      
      # 發送下班打卡請求
      clock_out_response = requests.post(f"{BASE_URL}/attendance/{attendance_id}/clock-out", json=clock_out_data)
      clock_out_response.raise_for_status()

      print(clock_out_response.json())
      
      success_count += 1
      print(f"成功建立打卡記錄 {success_count}/{len(records)} ({i+1}/{len(records)}): {record['UserName']} 在 {record['CaseName']} - {record['ClockInTime'].strftime('%Y-%m-%d')}")
      
    except Exception as e:
      error_count += 1
      print(f"建立打卡記錄失敗 ({i+1}/{len(records)}): {str(e)}")
  
  print(f"完成! 成功: {success_count}, 失敗: {error_count}")
  return success_count, error_count

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

# # 主函數
# def main(num_records=50, date_range_days=30, post_to_api=True):
#   print("開始建立假資料...")
  
#   # 建立使用者
#   if post_to_api:
#     create_fake_users()
    
#     # 建立案件
#     create_fake_cases()
  
#   # 生成打卡資料
#   print(f"生成打卡資料... (約 {num_records} 筆記錄，時間範圍: {date_range_days} 天)")
#   attendance_records = generate_attendance_data(num_records, date_range_days)
  
#   # 顯示生成的資料摘要
#   case_summary = {}
#   user_summary = {}
#   date_summary = {}
  
#   for record in attendance_records:
#     # 累計使用者資料
#     user_id = record["UserID"]
#     user_name = record["UserName"]
#     if user_id not in user_summary:
#       user_summary[user_id] = {
#         "name": user_name,
#         "count": 0,
#         "total_hours": 0,
#         "cases": set()
#       }
    
#     user_summary[user_id]["count"] += 1
#     user_summary[user_id]["total_hours"] += record["WorkHours"]
#     user_summary[user_id]["cases"].add(record["CaseID"])
    
#     # 累計案件資料
#     case_id = record["CaseID"]
#     case_name = record["CaseName"]
#     if case_id not in case_summary:
#       case_summary[case_id] = {
#         "name": case_name,
#         "count": 0,
#         "total_hours": 0,
#         "users": set()
#       }
    
#     case_summary[case_id]["count"] += 1
#     case_summary[case_id]["total_hours"] += record["WorkHours"]
#     case_summary[case_id]["users"].add(user_id)
    
#     # 累計日期資料
#     date_str = record["ClockInTime"].strftime("%Y-%m-%d")
#     if date_str not in date_summary:
#       date_summary[date_str] = {
#         "count": 0,
#         "total_hours": 0,
#         "users": set()
#       }
    
#     date_summary[date_str]["count"] += 1
#     date_summary[date_str]["total_hours"] += record["WorkHours"]
#     date_summary[date_str]["users"].add(user_id)
  
#   # 顯示統計資料
#   print(f"\
# 生成了 {len(attendance_records)} 筆打卡記錄")
  
#   print("\
# 使用者打卡統計:")
#   for user_id, data in user_summary.items():
#     print(f"{data['name']} - {data['count']} 筆記錄，總工時: {data['total_hours']:.2f} 小時，參與案件數: {len(data['cases'])}")
  
#   print("\
# 案件打卡統計:")
#   for case_id, data in case_summary.items():
#     print(f"[案件 {case_id}] {data['name']} - {data['count']} 筆記錄，總工時: {data['total_hours']:.2f} 小時，參與人數: {len(data['users'])}")
  
#   # 發送打卡資料到API
#   if post_to_api:
#     print("\
# 發送打卡資料到API...")
#     success, failed = post_attendance_data(attendance_records)
#     print(f"完成! 成功: {success}, 失敗: {failed}")
  
#   print("假資料生成完成!")
#   return attendance_records

if __name__ == "__main__":

  rec=generate_attendance_data(30,20)
  post_attendance_data(rec)
  # import argparse
  
  # parser = argparse.ArgumentParser(description="生成出勤記錄假資料")
  # parser.add_argument("-n", "--num-records", type=int, default=50, help="要生成的記錄總數（預設：50）")
  # parser.add_argument("-d", "--days", type=int, default=30, help="日期範圍（天數，預設：30）")
  # parser.add_argument("-p", "--post", action="store_true", help="是否將資料發送到API")
  # parser.add_argument("-o", "--output", type=str, help="將生成的資料保存到JSON檔案（選填）")
  
  # args = parser.parse_args()
  
  # # 生成資料
  # records = main(args.num_records, args.days, args.post)
  
  # # 如果指定了輸出檔案，將資料保存為JSON
  # if args.output:
  #   import json
  #   from datetime import datetime
    
  #   # 將datetime對象轉換為字符串
  #   def datetime_converter(o):
  #     if isinstance(o, datetime):
  #       return o.isoformat()
  #     if isinstance(o, set):
  #       return list(o)
    
  #   with open(args.output, 'w', encoding='utf-8') as f:
  #     json.dump(records, f, ensure_ascii=False, indent=2, default=datetime_converter)
  #   print(f"資料已保存到 {args.output}")

