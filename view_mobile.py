import streamlit as st
# import requests
import base64
import pytz
import time
from datetime import datetime, timedelta
from api import (
    create_clock_in,
    create_clock_out,
    get_attendance_by_user_id,
    get_attendance_by_id,
    get_cases,
    create_worklog,
    update_worklog,
    get_worklogs_by_user_id,
    get_case_by_id,
    create_material_borrow_log,
    get_materials,
    get_material_borrow_logs,
    create_material_return_log,
    get_material,
    create_leave_request,
    get_leave_requests,
    get_leave_request,
    get_leave_balance,
    get_user_leave_entitlements,
    get_equipments,
    get_equipment_detail,
    create_equipment_borrow_log,
    get_user_equipment_borrow_logs
)
from PIL import Image
import pandas as pd


if "safety_check_result" not in st.session_state:
    st.session_state.safety_check_result = False

if "worklog_added" not in st.session_state:
    st.session_state.worklog_added = False

taiwan_tz = pytz.timezone('Asia/Taipei')

# API_URL="http://localhost:8000"

@st.dialog(title="⚠️ 每日出工前勤前教育")
def safety_check():
    with st.container(border=True):
        st.markdown("##### 🔵火災、爆炸危害預防措施")
        fire_check = st.checkbox("我已確認以下所有預防措施", key="fire_safety")
        st.markdown("""
        - 在「嚴禁煙火」區或A類動火區域未經許可不可擅自動用火種
        - 在坑井、塔、槽、人孔、隧道及涵洞等侷限空間，未經測定可燃氣體不可動火
        - 使用各式砂輪機或研磨時火花四濺需戴防護具
        """)

    with st.container(border=True):
        st.markdown("##### 🔵電器機具設備、感電事故危害預防措施")
        electric_check = st.checkbox("我已確認以下所有預防措施", key="electric_safety")
        st.markdown("""
        - 配電工程活線或接近活線作業應使用防護具或有人監督
        - 停電作業工作之兩端或工作桿作業前應檢電，且掛妥接地線
        - 配電工程活線或接近活線作業防護措施需周全
        - 停電工作中於電路停電(開路)後，電路開關應上鎖或掛停電作業警示牌
        - 從插座取用電源要用插頭，不可以線端插入插座孔者(裸線作業)
        """)

    with st.container(border=True):
        st.markdown("##### 🔵墬落事故危害預防措施")
        fall_check = st.checkbox("我已確認以下所有預防措施", key="fall_safety")
        st.markdown("""
        - 高度在二公尺以上之工作場所應設有圍欄、握把、覆蓋等防護措施
        - 高架作業要依規定使用安全帶(安全繩索)或掛補助繩
        - 移開格子板或人孔護欄而於施工地點要設置警戒、圍欄等安全防護措施
        """)

    with st.container(border=True):
        st.markdown("##### 🔵施工架事故危害預防措施")
        scaffold_check = st.checkbox("我已確認以下所有預防措施", key="scaffold_safety")
        st.markdown("""
        - 要使用有防滑鋁梯或梯架、鷹架、施工架腳部要有保護措施等妥當器具
        - 施工架應設置護欄、踏板、爬梯及扶手
        - 高架作業時，不可隨意拋擲工具、器材、物料
        """)

    with st.container(border=True):
        st.markdown("##### 🔵起重吊掛事故危害預防措施")
        crane_check = st.checkbox("我已確認以下所有預防措施", key="crane_safety")
        st.markdown("""
        - 吊臂工程車不可擅自改造附加設備從事高架作業
        """)

    with st.container(border=True):
        st.markdown("##### 🔵安全帶、安全帽等安全配備")
        equipment_check = st.checkbox("我已確認以下所有預防措施", key="equipment_safety")
        st.markdown("""
        - 作業場所工作人員要戴安全帽、繫妥頭帶、依規定裝束著裝
        """)

    with st.container(border=True):
        st.markdown("##### 🔵工作場所清潔與行為規範")
        other_check = st.checkbox("我已確認以下所有規範", key="other_safety")
        st.markdown("""
        - 每日工作完畢後，要清理工作現場廢棄物或廢棄物依規定分類
        - 不可於工作前、工作場所飲用含酒精性飲料及使用（吸）違禁品等
        - 在工作中，絕對禁止嬉戲、打鬧等不安全行為
        """)

    # 檢查是否所有安全項目都已確認
    all_safety_checks = [
        fire_check, electric_check, fall_check, scaffold_check,
        crane_check, equipment_check, other_check
    ]

    if all(all_safety_checks):
        if st.button("確認", type='primary', use_container_width=True):
            st.session_state.safety_check_result = True
            st.success("勤前教育已完成，上班打卡成功!")
            time.sleep(3)
            st.rerun()
    else:
        st.error("請確認所有安全項目!")


@st.dialog("📝 填寫施工日誌")
def worklog_add_page(attendance):

    selected_case_id = attendance["CaseID"]

    st.markdown("案件名稱")
    st.info(get_case_by_id(selected_case_id)["Name"])
    
    content = st.text_area("工作內容", height=100, placeholder="請輸入今日工作內容...")
    progress = st.slider("工作進度 (%)", 0, 100, 50)

    # work_hour = st.number_input("工作時數", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
    
    # 提交按鈕
    if st.button("新增日誌", type="primary", use_container_width=True):
        if not content:
            st.error("請輸入工作內容")
        else:
            # 準備資料
            data = {
                "CaseID": selected_case_id,
                "UserID": st.session_state.user_id,
                "Content": content,
                "Progress": progress
            }
            
            try:
                # 建立工作日誌
                result = create_worklog(data)
                st.success("日誌已新增成功，拍照打卡下班!")
                st.session_state.worklog_added=True
                st.rerun()
            except Exception as e:
                st.error(f"新增失敗: {str(e)}")


def calculate_work_hours(clock_in_time, clock_out_time):
    """計算工作時間"""
    if not clock_in_time or not clock_out_time:
        return None

    try:
        tz = pytz.timezone("Asia/Taipei")

        # 轉換 clock_in_time
        if isinstance(clock_in_time, str):
            clock_in_time = datetime.fromisoformat(clock_in_time.replace('Z', '+00:00'))
        if clock_in_time.tzinfo is None:
            clock_in_time = tz.localize(clock_in_time)

        # 轉換 clock_out_time
        if isinstance(clock_out_time, str):
            clock_out_time = datetime.fromisoformat(clock_out_time.replace('Z', '+00:00'))
        if clock_out_time.tzinfo is None:
            clock_out_time = tz.localize(clock_out_time)

        # 計算時間差
        time_diff = clock_out_time - clock_in_time
        total_seconds = time_diff.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        hours_float =total_seconds / 3600

        return f"{hours}小時{minutes}分鐘"

    except Exception as e:
        st.error(f"計算工作時間錯誤: {str(e)}")
        return "計算錯誤",None

def clock_in():
    st.subheader("上班簽到")

    st.markdown("---")
    
    # 初始化 session state 來存儲拍照時間
    if "clock_in_time" not in st.session_state:
        st.session_state.clock_in_time = None

    upload_photo = st.camera_input("📸 上班自拍照片:", key="clock_in_photo")

    cases=get_cases()

    case_options={case["CaseID"]:case["Name"] for case in cases}
    selected_case_id=st.selectbox("負責案件",options=list(case_options.keys()),format_func=lambda x: case_options.get(x,x))

    if upload_photo is not None:
        # 當照片被拍攝時，立即記錄時間
        if st.session_state.clock_in_time is None:
            st.session_state.clock_in_time = datetime.now(taiwan_tz)
            
        photo_base64 = base64.b64encode(upload_photo.read()).decode()
        
        if st.session_state.safety_check_result==False:
            if st.button("勤前教育訓練",type='primary',use_container_width=True):
                safety_check()
        else:
            st.markdown("上班打卡時間")
            # 使用保存的拍照時間，而不是當前時間
            formatted_time = st.session_state.clock_in_time.strftime("%Y-%m-%d %H:%M:%S")
            st.info(formatted_time)

            data={
                "CaseID":selected_case_id,
                "UserID":st.session_state.user_id,
                "IsTrained":True,
                "ClockInPhoto":photo_base64,
                # 使用保存的拍照時間
                "ClockInTime": formatted_time
            }

            create_clock_in(data)
            # 重置 session state
            st.session_state.safety_check_result=False
            st.session_state.clock_in_time = None
            st.rerun()

def clock_out(attendance_id , clock_in_time):
    st.subheader("下班簽退")
    
    st.markdown("---")

    attendance= get_attendance_by_id(attendance_id)

    dt = datetime.fromisoformat(clock_in_time)
    st.markdown("上班時間")
    st.info(dt.strftime("%Y-%m-%d %H:%M:%S"))

    if st.session_state.worklog_added==False:
        if st.button("填寫施工日誌",type='primary',use_container_width=True):
            worklog_add_page(attendance)

    else: 

        upload_photo = st.camera_input("📸 下班自拍照片:", key="clock_out_photo")
        
        if upload_photo is not None:

            photo_base64 = base64.b64encode(upload_photo.read()).decode()
            st.markdown("下班時間")
            st.info(datetime.now(taiwan_tz).strftime("%Y-%m-%d %H:%M:%S"))
            st.markdown("累計工作時數")
            work_hour=calculate_work_hours(clock_in_time,datetime.now(taiwan_tz))
            st.info(work_hour)

            # if st.session_state.worklog_added==False:
            #     # st.warning("請先填寫施工日誌!")
            #     if st.button("填寫施工日誌",type='primary',use_container_width=True):
            #         worklog_add_page(attendance,work_hour_float)

            # else:
                # if st.button("簽退",type='primary',use_container_width=True):
            data={
                "ClockOutPhoto":photo_base64
            }      
            create_clock_out(attendance_id,data)

            st.success("拍照打卡下班成功!")
            time.sleep(3)

            st.session_state.worklog_added=False
            st.rerun()

def attendance_page():

    res=get_attendance_by_user_id(st.session_state.user_id)

    if len(res)==0:
        with st.container(border=True):
            clock_in()
    else:

        if res[len(res)-1]["ClockOutTime"] is None:

            attendance_id=res[len(res)-1]["AttendanceID"]
            clock_in_time=res[len(res)-1]["ClockInTime"]

            with st.container(border=True):
                clock_out(attendance_id,clock_in_time)
        else:
            with st.container(border=True):
                clock_in()


def get_materail_id():

    import os
    from dotenv import load_dotenv
    load_dotenv()

    TEST_MODE=os.getenv("TEST_MODE")

    if TEST_MODE=="True":
        materials=get_materials()
        materials={material["MaterialID"]:material["Name"] for material in materials}
        material_id=st.selectbox("材料",options=list(materials.keys()),format_func=lambda x: materials.get(x,x))
        return material_id

    else:

        from utils_qrcode import process_image
        file=st.camera_input("📸 拍照掃描QR碼",key="material_camera")

        if file is not None:
            
            results, gray, binary = process_image(Image.open(file))
            
            if results:
                for i, result in enumerate(results, 1):
                    st.success(f"成功掃描 QR 碼:")
                    for key, value in result.items():
                        st.write(f"**{key}:** {value}")
                        if key=="編碼":
                            material_id=value
                            return material_id
            else:
                return None
                        
def material_page():

    with st.container(border=True):
        

        cases=get_cases()

        case_options={case["CaseID"]:case["Name"] for case in cases}
        selected_case_id=st.selectbox("負責案件",options=list(case_options.keys()),format_func=lambda x: case_options.get(x,x))

        material_id=get_materail_id()

        if material_id is None:
            st.warning("未檢測到QR碼，請調整相機角度和距離")
            return

        material=get_material(material_id)
        if material is None:
            st.warning("未找到該材料")
            return
        else:
            st.write(material["Name"])

        num=st.number_input("數量",min_value=1,value=1,max_value=material["StockQuantity"])

        if st.button("借用",type="primary",use_container_width=True):
            data={
                "UserID":st.session_state.user_id,
                "CaseID":selected_case_id,
                "MaterialID":material_id,
                "Quantity_Out":num,
                # "Status":"出庫"
            }
            res=create_material_borrow_log(data)
            if "LogID" in res:
                st.success("借用成功")
                # st.rerun()

@st.fragment
def material_return_page():
    inventorys=get_material_borrow_logs(st.session_state.user_id)
    df_inventory=pd.DataFrame(inventorys)
    df_show=df_inventory[["LogID","case_name","material_name","Quantity_Out","Quantity_In","CreateTime"]]
    df_inventory["CreateTime"] = pd.to_datetime(df_inventory["CreateTime"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    # st.dataframe(df_show,hide_index=True,column_config={
    #     "LogID":"借出編號",
    #     "case_name":"案件名稱",
    #     "material_name":"材料名稱",
    #     "Quantity_Out":"借出數量",
    #     "Quantity_In":"歸還數量",
    #     "Status":"狀態",
    #     "CreateTime":"借出時間"
    # })

    #filter Quantity_In==null
    df_inventory=df_inventory[df_inventory['Quantity_In'].isnull()]
    

    for index,inventory in df_inventory.iterrows():
        with st.container(border=True):
            # 主標題 - 編號（票號 📄）
            st.markdown(f"**📄 編號:** `{inventory['LogID']}`")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**📁 案件:** {inventory['case_name']}")
                st.markdown(f"**🔧 名稱:** {inventory['material_name']}")

            with col2:
                st.markdown(f"**📦 借出:** {inventory['Quantity_Out']}")
                st.markdown(f"**⏰ 借出時間:** {inventory['CreateTime']}")

            # st.markdown(f"**歸還數量:** {inventory['Quantity_In']}")
            # 處理型別，確保 slider 參數皆為 int
            max_quantity = int(inventory['Quantity_Out']) if not pd.isnull(inventory['Quantity_Out']) else 0
            default_value = inventory['Quantity_In']
            if pd.isnull(default_value):
              default_value = 0
            else:
              default_value = int(default_value)
            return_quantity = st.slider(
              "剩餘數量",
              min_value=0,
              max_value=max_quantity,
              value=default_value,
              key=f"return_quantity_{inventory['LogID']}"
            )

            if st.button("歸還",type="primary",use_container_width=True,key=f"return_button_{inventory['LogID']}"):
              data={
                "LogID":inventory['LogID'],
                "Quantity_In":return_quantity
              }
              res=create_material_return_log(data)
              if "LogID" in res:
                st.success("歸還成功")
                time.sleep(3)
                st.rerun()



def get_equipment_id(key_suffix=""):
    """獲取機具 ID 的函數
    
    Args:
        key_suffix: 用於區分不同頁面的元素的後綴
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()

    TEST_MODE = os.getenv("TEST_MODE")

    if TEST_MODE == "True":
        equipments = get_equipments()
        equipment_options = {equipment["EquipmentID"]: equipment["Name"] for equipment in equipments}
        equipment_id = st.selectbox(
            "機具", 
            options=list(equipment_options.keys()), 
            format_func=lambda x: equipment_options.get(x, x),
            key=f"equipment_select_{key_suffix}"
        )
        return equipment_id
    else:
        from utils_qrcode import process_image
        file = st.camera_input(
            "📸 拍照掃描QR碼", 
            key=f"equipment_camera_{key_suffix}"
        )

        if file is not None:
            results, gray, binary = process_image(Image.open(file))
            
            if results:
                for i, result in enumerate(results, 1):
                    st.success(f"成功掃描 QR 碼:")
                    for key, value in result.items():
                        st.write(f"**{key}:** {value}")
                        if key == "編碼":
                            equipment_id = value
                            return equipment_id
            else:
                return None

@st.fragment
def equipment_borrow_page():
    """機具借用頁面"""
    with st.container(border=True):
        st.subheader("機具借用")
        
        # 獲取案件列表
        cases = get_cases()
        case_options = {case["CaseID"]: case["Name"] for case in cases}
        selected_case_id = st.selectbox("負責案件", options=list(case_options.keys()), format_func=lambda x: case_options.get(x, x), key="borrow_case")
        
        # 獲取機具 ID
        equipment_id = get_equipment_id(key_suffix="borrow")
        
        if equipment_id is None:
            st.warning("未檢測到QR碼，請調整相機角度和距離")
            return
        
        # 獲取機具詳情
        try:
            equipment = get_equipment_detail(equipment_id)
            if equipment is None:
                st.warning("未找到該機具")
                return
            
            # 顯示機具資訊
            st.write(f"**機具名稱:** {equipment['Name']}")
            st.write(f"**機具狀態:** {equipment['Status']}")
            
            # 檢查機具是否可借用
            if equipment['Status'] != "可用":
                st.error(f"該機具目前狀態為 {equipment['Status']}，不可借用")
                return
            
            # 借用數量
            quantity = st.number_input("借用數量", min_value=1, value=1, step=1)
            
            # 備註
            note = st.text_area("備註說明", placeholder="請輸入借用用途或其他說明...")
            
            # 提交按鈕
            if st.button("確認借用", type="primary", use_container_width=True):
                # 準備資料
                data = {
                    "EquipmentID": equipment_id,
                    "UserID": st.session_state.user_id,
                    "CaseID": selected_case_id,
                    "ActionType": "借用",
                    "Quantity": quantity,
                    "Note": note
                }
                
                try:
                    # 呼叫 API 進行借用
                    result = create_equipment_borrow_log(data)
                    if "LogID" in result:
                        st.success(f"借用成功！記錄編號: {result['LogID']}")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"借用失敗: {str(e)}")
        except Exception as e:
            st.error(f"獲取機具資訊失敗: {str(e)}")

@st.fragment
def equipment_return_page():
    """機具歸還頁面 - 顯示用戶所有借用的機具列表"""
    st.subheader("機具歸還")
    
    # 獲取用戶借用的機具記錄
    try:
        borrow_logs = get_user_equipment_borrow_logs(st.session_state.user_id)
        
        if not borrow_logs:
            st.info("您目前沒有需要歸還的機具")
            return
            
        # 轉換為 DataFrame 方便處理
        df_borrow = pd.DataFrame(borrow_logs)
        
        # 處理日期時間格式
        if 'ActionTime' in df_borrow.columns:
            df_borrow["ActionTime"] = pd.to_datetime(df_borrow["ActionTime"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # 篩選出未歸還的記錄（借用類型）
        df_borrow = df_borrow[df_borrow['ActionType'] == "借用"]
        
        if df_borrow.empty:
            st.info("您目前沒有需要歸還的機具")
            return
        
        # 顯示每一筆借用記錄
        for index, borrow in df_borrow.iterrows():
            with st.container(border=True):
                # 主標題 - 編號
                st.markdown(f"**📄 記錄編號:** `{borrow['LogID']}`")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🔧 機具名稱:** {borrow['EquipmentName']}")
                    if 'case_name' in borrow and borrow['case_name']:
                        st.markdown(f"**📁 案件:** {borrow['case_name']}")
                
                with col2:
                    st.markdown(f"**📦 借用數量:** {borrow['Quantity']}")
                    st.markdown(f"**⏰ 借用時間:** {borrow['ActionTime']}")
                
                if 'Note' in borrow and borrow['Note']:
                    st.markdown(f"**📝 借用備註:** {borrow['Note']}")
                
                # 歸還備註
                note = st.text_area("歸還備註", 
                                  placeholder="請輸入機具狀況或其他說明...", 
                                  key=f"return_note_{borrow['LogID']}")
                
                # 提交按鈕
                if st.button("確認歸還", 
                           type="primary", 
                           use_container_width=True, 
                           key=f"return_button_{borrow['LogID']}"):
                    # 準備資料
                    data = {
                        "EquipmentID": borrow['EquipmentID'],
                        "UserID": st.session_state.user_id,
                        "ActionType": "歸還",
                        "Quantity": 1,  # 機具歸還固定為 1
                        "Note": note
                    }
                    
                    # 如果有案件 ID，加入資料
                    if 'CaseID' in borrow and borrow['CaseID']:
                        data["CaseID"] = borrow['CaseID']
                    
                    try:
                        # 呼叫 API 進行歸還
                        result = create_equipment_borrow_log(data)
                        if "LogID" in result:
                            st.success(f"歸還成功！記錄編號: {result['LogID']}")
                            time.sleep(2)
                            st.rerun()
                    except Exception as e:
                        st.error(f"歸還失敗: {str(e)}")
    except Exception as e:
        st.error(f"獲取機具資訊失敗: {str(e)}")


# def equipment_page():
#     """設備借用歸還頁面"""
#     tab1, tab2 = st.tabs(["機具借用", "機具歸還"])
    
#     with tab1:
#         equipment_borrow_page()
    
#     with tab2:
#         equipment_return_page()

# @st.fragment
def leave_request_page():
    """請假申請頁面"""

    if "default_start_time" not in st.session_state:
        st.session_state.default_start_time = datetime.strptime("08:00", "%H:%M").time()  # 上午8.00
    if "default_end_time" not in st.session_state:
        st.session_state.default_end_time = datetime.strptime("17:00", "%H:%M").time()  # 下午5.00

    default_start_time=st.session_state.default_start_time
    default_end_time=st.session_state.default_end_time

    # 請假表單
    with st.container(border=True):
        # st.markdown("#### 填寫請假資訊")
        
        leave_type = st.selectbox(
            "請假類型",
            options=[
                "annual_special", 
                "personal", 
                "sick"
            ],
            format_func=lambda x: {
                "annual_special": "特別休假",
                "personal": "事假",
                "sick": "病假"
            }.get(x, x)
        )

        entitlements=get_user_leave_entitlements(st.session_state.user_id, datetime.now(taiwan_tz).year)
        
        # 顯示請假配額和已使用數
        if entitlements and len(entitlements) > 0:
            entitlement = entitlements[0]
            
            leave_info = {
                "annual_special": {
                    "name": "特別休假",
                    "total": float(entitlement.get("AnnualSpecialLeave", 0)),
                    "used": float(entitlement.get("AnnualSpecialLeaveUsed", 0))
                },
                "personal": {
                    "name": "事假",
                    "total": float(entitlement.get("PersonalLeave", 0)),
                    "used": float(entitlement.get("PersonalLeaveUsed", 0))
                },
                "sick": {
                    "name": "病假",
                    "total": float(entitlement.get("SickLeave", 0)),
                    "used": float(entitlement.get("SickLeaveUsed", 0))
                }
            }
            
            selected_leave = leave_info.get(leave_type, {})
            if selected_leave:
                st.markdown("**"+str(selected_leave['total']-selected_leave['used'])+"** 天可用")
                # col1, col2, col3 = st.columns(3,border=True)
                # with col1:
                #     st.metric("總天數", f"{selected_leave['total']:.1f}")
                # with col2:
                #     st.metric("已使用", f"{selected_leave['used']:.1f}")
                # with col3:
                #     remaining = selected_leave['total'] - selected_leave['used']
                #     st.metric("剩餘", f"{remaining:.1f}")
        
        # 請假日期
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日期", datetime.now(taiwan_tz).date())
        with col2:
            end_date = st.date_input("結束日期", datetime.now(taiwan_tz).date())
        
        # 請假時間
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("開始時間",default_start_time)
        with col2:
            end_time = st.time_input("結束時間",default_end_time)
        # 請假時數計算
        if start_date == end_date:
            # 同一天，計算時間差
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            hours_diff = (end_datetime - start_datetime).total_seconds() / 3600

            # 扣除午休時間 (假設午休時間為 12:00-13:00)
            if start_time <= datetime.strptime("12:00", "%H:%M").time() and end_time >= datetime.strptime("13:00", "%H:%M").time():
                hours_diff -= 1
            leave_hours = min(8, max(0, hours_diff))
        else:
            # 跨天，計算天數 * 8小時
            days_diff = (end_date - start_date).days + 1
            leave_hours = days_diff * 8
        

        st.info(f"請假時數: {leave_hours:.1f} 小時")
        
        # 請假原因
        reason = st.text_area("請假原因")
        
        # 提交按鈕
        submitted = st.button("提交請假申請", type="primary", use_container_width=True)
        
        if submitted:
            # 準備請假資料
            leave_data = {
                "UserID": st.session_state.user_id,
                "LeaveType": leave_type,
                "StartDate": start_date.isoformat(),
                "EndDate": end_date.isoformat(),
                "StartTime": start_time.isoformat(),
                "EndTime": end_time.isoformat(),
                "LeaveHours": float(leave_hours),
                "Reason": reason
            }
            st.write(leave_data)
            try:
                # 提交請假申請
                response = create_leave_request(leave_data)
                if "RequestID" in response:
                    st.success(f"請假申請已成功提交！申請編號: {response['RequestID']}")
                    # 清空表單或重新載入頁面
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"請假申請提交失敗: {response}")
            except Exception as e:
                st.error(f"請假申請提交失敗: {str(e)}")

with st.container(border=True):
    # myradio=st.radio("選擇功能",("打卡","材料借用","材料歸還","設備借用","設備歸還"),horizontal=True)
    myradio=st.selectbox("選擇功能",("打卡簽到","材料借用","材料歸還","機具借用","機具歸還","請假申請"))

if myradio=="打卡簽到":
    attendance_page()
elif myradio=="請假申請":
    leave_request_page()
# elif myradio=="請假紀錄":
#     pass
    # leave_history_page()
elif myradio=="材料借用":
    material_page()
elif myradio=="材料歸還":
    material_return_page()
elif myradio=="機具借用":
    equipment_borrow_page()
elif myradio=="機具歸還":
    equipment_return_page()