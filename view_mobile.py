import streamlit as st
import requests
import base64
import pytz
from datetime import datetime, timedelta
from api import (
    create_clock_in,
    create_clock_out,
    get_attendance_by_user_id,
    get_cases,
    get_worklogs,
    create_worklog,
    update_worklog,
    delete_worklog,
    get_worklogs_by_user_id
)

if "safety_check_result" not in st.session_state:
    st.session_state.safety_check_result = False

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

    if st.button("確認", type='primary', use_container_width=True):
        st.session_state.safety_check_result = True
        st.rerun()

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

        return f"{hours}小時{minutes}分鐘"

    except Exception as e:
        st.error(f"計算工作時間錯誤: {str(e)}")
        return "計算錯誤"

def clock_in():
    st.subheader("上班簽到")
    st.markdown("### 📸 上班自拍照片")
    upload_photo = st.camera_input("照片:", key="clock_in_photo")

    cases=get_cases()

    case_options={case["CaseID"]:case["Name"] for case in cases}
    selected_case_id=st.selectbox("選擇案件",options=list(case_options.keys()),format_func=lambda x: case_options.get(x,x))

    if upload_photo is not None:
        photo_base64 = base64.b64encode(upload_photo.read()).decode()
        
        if st.session_state.safety_check_result==False:
            if st.button("執行勤前教育訓練"):
                safety_check()
        else:
            st.markdown("上班打卡時間")
            now = datetime.now(taiwan_tz)
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            st.info(formatted_time)

            if st.button("簽到",type='primary',use_container_width=True):

                data={
                    "CaseID":selected_case_id,
                    "UserID":st.session_state.user_id,
                    "IsTrained":True,
                    "ClockInPhoto":photo_base64
                }

                create_clock_in(data)

                st.session_state.safety_check_result=False
                st.rerun()

def clock_out(attendance_id , clock_in_time):
    st.subheader("下班簽退")
    dt = datetime.fromisoformat(clock_in_time)
    st.markdown("上班時間")
    st.info(dt.strftime("%Y-%m-%d %H:%M:%S"))

    st.markdown("### 📸 下班自拍照片")
    upload_photo = st.camera_input("照片:", key="clock_out_photo")
    
    if upload_photo is not None:
        photo_base64 = base64.b64encode(upload_photo.read()).decode()
        st.markdown("下班時間")
        st.info(datetime.now(taiwan_tz).strftime("%Y-%m-%d %H:%M:%S"))
        st.markdown("累計工作時數")
        st.info(str(calculate_work_hours(clock_in_time,datetime.now(taiwan_tz))))

        if st.button("簽退",type='primary',use_container_width=True):
            data={
                "ClockOutPhoto":photo_base64
            }      
            create_clock_out(attendance_id,data)
            st.rerun()

@st.dialog("編輯日誌")
def edit_worklog(log):

    # 工作內容輸入
    edit_content = st.text_area("工作內容", value=log[0].get('Content', ''), height=100, key="edit_content")
    edit_progress = st.slider("工作進度 (%)", 0, 100, int(log[0].get('Progress', 50)), key="edit_progress")
    edit_work_hour = st.number_input("工作時數", min_value=0.0, max_value=24.0, value=float(log[0].get('WorkHour', 8.0)), step=0.5, key="edit_work_hour")
    
    # 提交按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("取消", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("更新", type="primary", use_container_width=True):
            if not edit_content:
                st.error("請輸入工作內容")
            else:
                # 準備資料
                data = {
                    "Content": edit_content,
                    "Progress": edit_progress,
                    "WorkHour": edit_work_hour
                }
                
                try:
                    # 更新工作日誌
                    update_worklog(log[0].get('WorkLogID'), data)
                    st.success("日誌已更新成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"更新失敗: {str(e)}")

def attendance_page():

    res=get_attendance_by_user_id(st.session_state.user_id)

    if res[len(res)-1]["ClockOutTime"] is None:

        attendance_id=res[len(res)-1]["AttendanceID"]
        clock_in_time=res[len(res)-1]["ClockInTime"]

        with st.container(border=True):
            clock_out(attendance_id,clock_in_time)
    else:
        with st.container(border=True):
            clock_in()


def construction_page():
    # 取得案件列表
    cases = get_cases()
    case_options = {case["CaseID"]: case["Name"] for case in cases}
    work_date=datetime.now(taiwan_tz).date()

    today_log=get_worklogs_by_user_id(st.session_state.user_id,work_date)
    # 日誌操作區塊
    with st.container(border=True):
        
        st.subheader("施工日誌")
        if today_log:  # 今日已有回報，顯示已有內容
            
            st.info(f"今日已回報日誌 - {case_options.get(today_log[0].get('CaseID'), '未知案件')}")
            
            st.markdown(f"**工作內容:** {today_log[0].get('Content', '')}")
            st.markdown(f"**進度:** {today_log[0].get('Progress', 0)}%")
            st.markdown(f"**工作時數:** {today_log[0].get('WorkHour', 0)} 小時")
            st.markdown(f"**提交時間:** {today_log[0].get('LogTime', '')}")
            
            # 編輯按鈕
            if st.button("編輯日誌", type="primary", use_container_width=True):
                edit_worklog(today_log)
                # st.rerun()
        
        else:  # 今日尚未回報，顯示新增畫面
            # 選擇案件
            selected_case_id = st.selectbox(
                "選擇案件",
                options=list(case_options.keys()),
                format_func=lambda x: case_options.get(x, x)
            )
            
            content = st.text_area("工作內容", height=100, placeholder="請輸入今日工作內容...")
            progress = st.slider("工作進度 (%)", 0, 100, 50)
            work_hour = st.number_input("工作時數", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
            
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
                        "Progress": progress,
                        "WorkHour": work_hour,
                    }
                    
                    try:
                        # 建立工作日誌
                        result = create_worklog(data)
                        
                        st.success("日誌已新增成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"新增失敗: {str(e)}")
    

def material_page():
    st.title("材料借用歸還")
    st.write("這是材料借用歸還頁面")
    # 這裡可以添加材料借用歸還的相關功能

def equipment_page():
    st.title("設備借用歸還")
    st.write("這是設備借用歸還頁面")
    # 這裡可以添加設備借用歸還的相關功能

## 打卡、施工日誌、材料借用歸還、機器借用歸還

with st.container(border=True):
    myradio=st.radio("選擇功能",("打卡","日誌","材料","設備"),horizontal=True)

if myradio=="打卡":
    attendance_page()
elif myradio=="日誌":
    construction_page()
elif myradio=="材料":
    material_page()
elif myradio=="設備":
    equipment_page()