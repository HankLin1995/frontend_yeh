import streamlit as st
import pandas as pd
import requests
import os

from api import get_users, get_user, get_employee_detail, update_employee, create_employee

# 選擇目前作用中員工

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
        """)

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

# 顯示員工、薪資、證照(分成tab)

#emoji
st.markdown("")

selected_user=get_active_employee()

tab1, tab2, tab3 = st.tabs(["🧑‍💼基本資料", "🏅 證照", "💰 薪資"])

with tab1:
    employee = get_employee_detail(selected_user['UserID'])

    if not "detail" in employee:

        display_employee(employee)
    
        if st.sidebar.button("✏️ 編輯員工資料"):
            edit_employee_ui(employee)
        # if st.button("🗑️ 刪除員工"):
        #     delete_employee(employee["id"])
        #     st.success("員工資料已刪除！請重新整理頁面。")

    else:
        st.write("目前查無員工資料，請先設定員工資料。")
        if st.button("新增員工資料"):
            create_employee_ui(line_id=selected_user['UserID'])

with tab2:
    pass

with tab3:
    pass

def employee_main_page():
    users = get_users()
    lineid_options = [f"{u['UserName']} ({u['UserID']})" for u in users]
    selected = st.selectbox("選擇 LINE ID", lineid_options)
    selected_lineid = selected.split('(')[-1][:-1] if selected else None

    employees = get_employees()
    emp = next((e for e in employees if str(e.get('line_id')) == selected_lineid), None)
    
    if emp:
        st.success(f"已建立員工資料：{emp['name']}")
        tab1, tab2, tab3 = st.tabs(["基本資料", "證照", "薪資"])
        with tab1:
            st.subheader("員工基本資料")
            st.json(emp)
            with st.expander("編輯員工"):
                form = st.form("edit_employee")
                name = form.text_input("姓名", emp["name"])
                gender = form.selectbox("性別", ["男", "女"], index=0 if emp.get("gender", "男") == "男" else 1)
                birth_date = form.date_input("生日", pd.to_datetime(emp.get("birth_date", "1990-01-01")))
                phone = form.text_input("電話", emp.get("phone", ""))
                address = form.text_input("地址", emp.get("address", ""))
                hire_date = form.date_input("到職日", pd.to_datetime(emp.get("hire_date", "2023-01-01")))
                submitted = form.form_submit_button("更新")
                if submitted:
                    data = {"name": name, "line_id": selected_lineid, "gender": gender, "birth_date": str(birth_date), "phone": phone, "address": address, "hire_date": str(hire_date)}
                    update_employee(emp["id"], data)
                    st.success("更新成功！請重新整理頁面。")
            if st.button("刪除員工"):
                delete_employee(emp["id"])
                st.success("刪除成功！請重新整理頁面。")
        with tab2:
            st.subheader("證照 CRUD")
            certs = get_certificates(emp["id"])
            cert_df = pd.DataFrame(certs)
            st.dataframe(cert_df)
            with st.expander("新增證照"):
                form = st.form("create_cert")
                cert_name = form.text_input("證照名稱")
                issue_date = form.date_input("發證日")
                expiry_date = form.date_input("到期日")
                cert_url = form.text_input("證照連結")
                submitted = form.form_submit_button("新增")
                if submitted:
                    data = {"certificate_name": cert_name, "issue_date": str(issue_date), "expiry_date": str(expiry_date), "certificate_url": cert_url, "employee_id": emp["id"]}
                    create_certificate(data)
                    st.success("新增成功！請重新整理頁面。")
            cert_selected = st.selectbox("選擇證照", cert_df["certificate_name"]) if not cert_df.empty else None
            if cert_selected:
                cert = cert_df[cert_df["certificate_name"] == cert_selected].iloc[0]
                with st.expander("編輯證照"):
                    form = st.form("edit_cert")
                    cert_name = form.text_input("證照名稱", cert["certificate_name"])
                    issue_date = form.text_input("發證日", cert.get("issue_date", ""))
                    expiry_date = form.text_input("到期日", cert.get("expiry_date", ""))
                    cert_url = form.text_input("證照連結", cert.get("certificate_url", ""))
                    submitted = form.form_submit_button("更新")
                    if submitted:
                        data = {"certificate_name": cert_name, "issue_date": issue_date, "expiry_date": expiry_date, "certificate_url": cert_url}
                        update_certificate(cert["id"], data)
                        st.success("更新成功！請重新整理頁面。")
                if st.button("刪除證照"):
                    delete_certificate(cert["id"])
                    st.success("刪除成功！請重新整理頁面。")
        with tab3:
            st.subheader("薪資 CRUD")
            salaries = get_salaries(emp["id"])
            sal_df = pd.DataFrame(salaries)
            st.dataframe(sal_df)
            with st.expander("新增薪資"):
                form = st.form("create_salary")
                amount = form.number_input("金額", min_value=0)
                date = form.date_input("日期")
                submitted = form.form_submit_button("新增")
                if submitted:
                    data = {"employee_id": emp["id"], "amount": amount, "date": str(date)}
                    create_salary(data)
                    st.success("新增成功！請重新整理頁面。")
            sal_selected = st.selectbox("選擇日期", sal_df["date"] if not sal_df.empty else [], key="sal_edit")
            if sal_selected:
                sal = sal_df[sal_df["date"] == sal_selected].iloc[0]
                with st.expander("編輯薪資"):
                    form = st.form("edit_salary")
                    amount = form.number_input("金額", value=sal["amount"], min_value=0)
                    date = form.text_input("日期", sal["date"])
                    submitted = form.form_submit_button("更新")
                    if submitted:
                        data = {"amount": amount, "date": date}
                        update_salary(sal["id"], data)
                        st.success("更新成功！請重新整理頁面。")
    else:
        st.warning(f"此 LINE ID 尚未建立員工資料，請填寫下方表單建立：")
        with st.form("create_employee"):
            name = st.text_input("姓名")
            gender = st.selectbox("性別", ["男", "女"])
            birth_date = st.date_input("生日")
            phone = st.text_input("電話")
            address = st.text_input("地址")
            hire_date = st.date_input("到職日")
            submitted = st.form_submit_button("建立員工")
            if submitted:
                data = {"name": name, "line_id": selected_lineid, "gender": gender, "birth_date": str(birth_date), "phone": phone, "address": address, "hire_date": str(hire_date)}
                create_employee(data)
                st.success("建立成功！請重新整理頁面。")

# employee_main_page()
