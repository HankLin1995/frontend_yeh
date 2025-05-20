import streamlit as st
import pandas as pd
import datetime

from api import (
    BASE_URL,
    get_users,
    get_employee_detail,
    update_employee,
    create_employee,
    get_certificates,
    upload_certificate_file,
    delete_certificate,
    create_salary,
    get_salaries,
    delete_salary,
    get_attendance_by_user_id,
    get_cases
)

def format_hours_minutes(hours_float):
    hours = int(hours_float)
    minutes = int(round((hours_float - hours) * 60))
    return f"{hours}小時{minutes}分鐘"

def get_active_employee():
    
    with st.sidebar.container(border=True):

        users=get_users()
        user_name_list=[f"{u['UserName']}" for u in users]
        selected_lineid = st.selectbox("🆔 選擇 LINE ID", user_name_list)
        selected_user = next((u for u in users if u['UserName'] == selected_lineid), None)
        return selected_user

def display_employee(employee):

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
    #### 👤 員工基本資料

    **姓名**：{employee.get("name", "-")}  
    **性別**：{employee.get("gender", "-")}  
    **生日**：{employee.get("birth_date", "-")}  
    **身分證字號**：{employee.get("id_number", "-")}

    ---

    #### 📞 聯絡資訊

    **電話**：{employee.get("phone", "-")}  
    **地址**：{employee.get("address", "-")}

    ---

    #### 🧑‍💼 任職狀況

    **到職日**：{employee.get("hire_date", "-")}  
    **離職日**：{employee.get("termination_date", "-")}

    ---
            """)

        with col2:
            st.markdown(f"""
    #### 🚨 緊急聯絡人

    **姓名**：{employee.get("emergency_contact_name", "-")}  
    **電話**：{employee.get("emergency_contact_phone", "-")}  
    **關係**：{employee.get("emergency_contact_relation", "-")}  
    **地址**：{employee.get("emergency_contact_address", "-")}

    ---

    #### 🏥 健康與備註

    **病史**：{employee.get("medical_conditions", "-")}  
    **備註**：{employee.get("notes", "-")}

    ---
            """)
            display_salary_metric(employee)
    
        
    if st.button("✏️ 編輯員工資料",key="edit_employee"):
        edit_employee_ui(employee)

@st.dialog("✏️ 新增員工資料")
def create_employee_ui(line_id):
    form = st.form("create_employee_form")

    name = form.text_input("姓名", employee.get("name", ""))
    gender = form.selectbox("性別", ["男", "女"], index=0 if employee.get("gender") == "男" else 1)
    birth_date = form.date_input("生日", pd.to_datetime(employee.get("birth_date") or "1990-01-01"))
    id_number = form.text_input("身分證字號", employee.get("id_number") or "")
    address = form.text_input("地址", employee.get("address") or "")
    phone = form.text_input("電話", employee.get("phone") or "")
    hire_date = form.date_input("到職日", pd.to_datetime(employee.get("hire_date") or "2023-01-01"))
    termination_date = form.date_input("離職日", pd.to_datetime(employee.get("termination_date") or "2099-12-31")) if employee.get("termination_date") else form.date_input("離職日", pd.to_datetime("2099-12-31"))
    medical_conditions = form.text_area("病史", employee.get("medical_conditions") or "")
    emergency_contact_name = form.text_input("緊急聯絡人姓名", employee.get("emergency_contact_name") or "")
    emergency_contact_relation = form.text_input("緊急聯絡人關係", employee.get("emergency_contact_relation") or "")
    emergency_contact_address = form.text_input("緊急聯絡人地址", employee.get("emergency_contact_address") or "")
    emergency_contact_phone = form.text_input("緊急聯絡人電話", employee.get("emergency_contact_phone") or "")
    notes = form.text_area("備註", employee.get("notes") or "")
    submitted = form.form_submit_button("新增")
    if submitted:
        data = {
            "name": name,
            "line_id": line_id,
            "gender": gender,
            "birth_date": str(birth_date),
            "id_number": id_number,
            "address": address,
            "phone": phone,
            "hire_date": str(hire_date),
            "termination_date": str(termination_date) if termination_date else None,
            "medical_conditions": medical_conditions,
            "emergency_contact_name": emergency_contact_name,
            "emergency_contact_relation": emergency_contact_relation,
            "emergency_contact_address": emergency_contact_address,
            "emergency_contact_phone": emergency_contact_phone,
            "notes": notes,
        }
        # st.json(data)
        new_employee = create_employee(data)
        # st.write(new_employee)
        st.rerun()

@st.dialog("✏️ 編輯員工資料")
def edit_employee_ui(employee):
    # with st.container(border=True):
    form = st.form("edit_employee_form")
    name = form.text_input("姓名", employee.get("name", ""))
    gender = form.selectbox("性別", ["男", "女"], index=0 if employee.get("gender") == "男" else 1)
    birth_date = form.date_input("生日", pd.to_datetime(employee.get("birth_date") or "1990-01-01"))
    id_number = form.text_input("身分證字號", employee.get("id_number") or "")
    address = form.text_input("地址", employee.get("address") or "")
    phone = form.text_input("電話", employee.get("phone") or "")
    hire_date = form.date_input("到職日", pd.to_datetime(employee.get("hire_date") or "2023-01-01"))
    termination_date = form.date_input("離職日", pd.to_datetime(employee.get("termination_date") or "2099-12-31")) if employee.get("termination_date") else form.date_input("離職日", pd.to_datetime("2099-12-31"))
    medical_conditions = form.text_area("病史", employee.get("medical_conditions") or "")
    emergency_contact_name = form.text_input("緊急聯絡人姓名", employee.get("emergency_contact_name") or "")
    emergency_contact_relation = form.text_input("緊急聯絡人關係", employee.get("emergency_contact_relation") or "")
    emergency_contact_address = form.text_input("緊急聯絡人地址", employee.get("emergency_contact_address") or "")
    emergency_contact_phone = form.text_input("緊急聯絡人電話", employee.get("emergency_contact_phone") or "")
    notes = form.text_area("備註", employee.get("notes") or "")
    submitted = form.form_submit_button("更新")
    if submitted:
        data = {
            "name": name,
            "gender": gender,
            "birth_date": str(birth_date),
            "id_number": id_number,
            "address": address,
            "phone": phone,
            "hire_date": str(hire_date),
            "termination_date": str(termination_date) if termination_date else None,
            "medical_conditions": medical_conditions,
            "emergency_contact_name": emergency_contact_name,
            "emergency_contact_relation": emergency_contact_relation,
            "emergency_contact_address": emergency_contact_address,
            "emergency_contact_phone": emergency_contact_phone,
            "notes": notes,
        }
        update_employee(employee["id"], data)
        st.success("員工資料已更新！請重新整理頁面。")
        st.rerun()

@st.dialog("新增證照資料")
def create_certificate_ui(employee_id):

    certificate_name = st.text_input("證照名稱", "")
    issue_date = st.date_input("發證日 (YYYY-MM-DD)")
    expiry_date = st.date_input("到期日 (YYYY-MM-DD)")
    file = st.file_uploader("上傳證照檔案 (PDF/JPG/PNG)", type=["pdf", "jpg", "jpeg", "png"])
    submitted = st.button("新增")
    if submitted:
        if not certificate_name:
            st.error("請輸入證照名稱")
            return
        if not file:
            st.error("請上傳證照檔案")
            return
        file_bytes = (file.name, file, file.type)
        result = upload_certificate_file(
            employee_id=employee_id,
            file=file_bytes,
            certificate_name=certificate_name,
            issue_date=issue_date if issue_date else None,
            expiry_date=expiry_date if expiry_date else None
        )
        st.success("證照資料已新增！請重新整理頁面。")
        st.rerun()

def display_certificates_table_view(employee_id):
    df_cert = pd.DataFrame(get_certificates(employee_id))
    if df_cert.empty:
        st.warning("目前查無證照資料，請先設定證照資料。")
        return

    cols = st.columns(3)  # 每列顯示3張卡片，可依需求調整
    for idx, cert in df_cert.iterrows():
        with cols[idx % 3]:
            
            with st.container(border=True,height=500):
                st.markdown("🏅 " + cert['certificate_name'])
                st.write("生效日",cert['issue_date'],"~","到期日",cert['expiry_date'])
                st.image(BASE_URL+"/"+cert['certificate_url'])
            
            # Streamlit 不支援 form button in markdown, 改用 st.button
            if st.button("刪除"+cert['certificate_name'], key=f"delete_cert_{cert['id']}"):
                delete_certificate(int(cert["id"]))
                st.success("證照資料已刪除！請重新整理頁面。")
                st.rerun()

def display_certificates_df_view(employee_id):
    
    df_cert = pd.DataFrame(get_certificates(employee_id))
    
    if df_cert.empty:
        st.write("目前查無證照資料，請先設定證照資料。")
    else:

        event = st.dataframe(
            df_cert,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row"
        )

        select_users = event.selection.rows
        filtered_df = df_cert.iloc[select_users]

        if filtered_df.empty:
            pass
        else:
            if st.button("刪除證照",key="delete_certificate"):
                delete_certificate(int(filtered_df["id"]))
                st.success("證照資料已刪除！請重新整理頁面。")
                st.rerun()

@st.dialog("➕ 新增薪資紀錄")
def create_salary_ui(employee_id,df_salary):
    
    if not df_salary.empty:
        old_daily_wage = df_salary['new_daily_wage'].iloc[-1]
    else:
        old_daily_wage = 0
    
    new_daily_wage = st.number_input("薪資金額", min_value=0, value=30000)
    salary_date = st.date_input("薪資日期", value=datetime.date.today())
    note = st.text_input("備註")

    if st.button("新增"):

        create_salary({
            'employee_id': employee_id,
            'adjustment_date': str(salary_date),
            'new_daily_wage': new_daily_wage,
            'old_daily_wage':old_daily_wage,
            'adjustment_reason': note
        })
        st.success("薪資紀錄已新增！請重新整理頁面。")
        st.rerun()



def display_salary_metric(employee):

    salaries = get_salaries(employee['id'])
    df_salary = pd.DataFrame(salaries)
    if df_salary.empty:
        st.warning("目前查無薪資資料。")
    else:

        diff=df_salary['new_daily_wage'].iloc[-1]-df_salary['old_daily_wage'].iloc[-1]
        # 顯示目前薪資

        # with st.container(border=True):
        if df_salary['old_daily_wage'].iloc[-1]!=0:
            st.metric("目前薪資", f"{int(df_salary['new_daily_wage'].iloc[-1]):,}", int(diff))
        else:
            st.metric("目前薪資", f"{int(df_salary['new_daily_wage'].iloc[-1]):,}")

        st.badge("生效日:"+df_salary['adjustment_date'].iloc[-1],color="green")

def display_salaries():
    st.markdown("### 💰 薪資紀錄")

    salaries = get_salaries(employee['id'])
    df_salary = pd.DataFrame(salaries)
    if df_salary.empty:
        st.warning("目前查無薪資資料。")
    else:
        st.dataframe(
            df_salary,
            column_config={
                "old_daily_wage": st.column_config.NumberColumn("原始薪資"),
                "new_daily_wage": st.column_config.NumberColumn("目前薪資"),
                "adjustment_date": st.column_config.TextColumn("更動日期"),
                "adjustment_reason": st.column_config.TextColumn("備註"),
                "id": None,
                "employee_id":None
            },
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row"
        )

        if st.button("刪除最近一筆",key="delete_salary"):
            delete_salary(len(df_salary))
            st.success("證照資料已刪除！請重新整理頁面。")
            st.rerun()

    st.markdown("---")

    return df_salary

#emoji
st.markdown("")

selected_user=get_active_employee()

tab1, tab2, tab3, tab4 = st.tabs(["🧑‍💼基本資料", "🏅 證照", "💰 薪資","⏰ 打卡紀錄"])

with tab1:
    employee = get_employee_detail(selected_user['UserID'])

    if not "detail" in employee:

        display_employee(employee)

    else:
        st.warning("目前查無員工資料，請先設定員工資料。")
        if st.button("新增員工資料"):
            create_employee_ui(line_id=selected_user['UserID'])

with tab2:

    if not "detail" in employee:
        display_certificates_table_view(employee['id'])

        st.markdown("---")

        if st.button("➕ 新增證照資料"):
            create_certificate_ui(employee['id'])

    else:
        st.warning("目前查無資料。")
        
with tab3:
    if not "detail" in employee:
        df_salary=display_salaries()
        if st.button("➕ 新增薪資紀錄"):
            create_salary_ui(employee['id'],df_salary)

    else:
        st.warning("目前查無員工資料，請先設定員工資料。")

with tab4:
    data=get_attendance_by_user_id(selected_user['UserID'])

    df_attendance=pd.DataFrame(data)

    df_cases=pd.DataFrame(get_cases())

    if df_attendance.empty:
        st.warning("目前查無打卡資料。")
    else:

        df_attendance['CaseID']=df_attendance['CaseID'].apply(lambda x: df_cases[df_cases['CaseID']==x]['Name'].values[0])

        #照片用image顯示
        df_attendance['ClockInPhoto']=df_attendance['ClockInPhoto'].apply(lambda x: BASE_URL + "/" + x.split("/")[-1])  # 只取檔名部分)
        df_attendance['ClockOutPhoto']=df_attendance['ClockOutPhoto'].apply(lambda x: BASE_URL + "/" + x.split("/")[-1])  # 只取檔名部分)
        
        import datetime

        # 將字串轉為 datetime 物件，再轉為指定格式的字串
        df_attendance['ClockInTime'] = df_attendance['ClockInTime'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        )

        df_attendance['ClockOutTime'] = df_attendance['ClockOutTime'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        )

        #換算工時
        df_attendance['ClockInTime_calc'] = pd.to_datetime(df_attendance['ClockInTime'])
        df_attendance['ClockOutTime_calc'] = pd.to_datetime(df_attendance['ClockOutTime'])
        df_attendance['WorkHours'] = round((df_attendance['ClockOutTime_calc'] - df_attendance['ClockInTime_calc']).dt.total_seconds() / 3600,4)

        df_attendance['WorkHours'] = df_attendance['WorkHours'].apply(format_hours_minutes)

        st.dataframe(df_attendance,hide_index=True,column_config={
            "UserID":None,
            "AttendanceID":None,
            "CaseID":st.column_config.TextColumn("案件",),
            "ClockInTime":st.column_config.TextColumn("上班時間"),
            "ClockOutTime":st.column_config.TextColumn("下班時間"),
            "ClockInPhoto": st.column_config.ImageColumn("上班照片",width="small"),
            "ClockOutPhoto": st.column_config.ImageColumn("下班照片",width="small"),
            "IsTrained":"是否訓練",
            "ClockInTime_calc":None,
            "ClockOutTime_calc":None,
            "WorkHours":st.column_config.TextColumn("工時")
        })

    # if len(df_attendance)==0:
    #     st.warning("目前查無打卡資料。")
    # else:
    #     for idx,record in df_attendance.iterrows():
    #         with st.expander(f"Attendance #{record['AttendanceID']} — {record['ClockInTime']}"):
    #             st.write(f"**Is Trained**: {record['IsTrained']}")
    #             col1,col2=st.columns(2)
    #             with col1:
    #                 st.image(f"{BASE_URL}/{record['ClockInPhoto']}", caption=record['ClockInTime'])
    #             with col2:
    #                 st.image(f"{BASE_URL}/{record['ClockOutPhoto']}", caption=record['ClockOutTime'])
