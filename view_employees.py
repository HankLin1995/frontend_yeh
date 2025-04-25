import streamlit as st
import pandas as pd


from api import (
    BASE_URL,
    get_users,
    get_employee_detail,
    update_employee,
    create_employee,
    get_certificates,
    upload_certificate_file,
    delete_certificate
)

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
def display_certificates(employee_id):
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

# def display_certificates(employee_id):
    
#     df_cert = pd.DataFrame(get_certificates(employee_id))
    
#     if df_cert.empty:
#         st.write("目前查無證照資料，請先設定證照資料。")
#     else:

#         event = st.dataframe(
#             df_cert,
#             hide_index=True,
#             on_select="rerun",
#             selection_mode="multi-row"
#         )

#         select_users = event.selection.rows
#         filtered_df = df_cert.iloc[select_users]

#         if filtered_df.empty:
#             pass
#         else:
#             if st.button("刪除證照",key="delete_certificate"):
#                 delete_certificate(int(filtered_df["id"]))
#                 st.success("證照資料已刪除！請重新整理頁面。")
#                 st.rerun()

# 顯示員工、薪資、證照(分成tab)

#emoji
st.markdown("")

selected_user=get_active_employee()

tab1, tab2, tab3 = st.tabs(["🧑‍💼基本資料", "🏅 證照", "💰 薪資"])

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
        display_certificates(employee['id'])

        st.markdown("---")

        if st.button("➕ 新增證照資料"):
            create_certificate_ui(employee['id'])

    else:
        st.warning("目前查無資料。")
        
with tab3:
    pass
