import streamlit as st

st.set_page_config(page_title="工程管理系統", layout="wide")

user_page=st.Page("view_users.py",title="用戶管理",icon=":material/account_circle:")
group_page=st.Page("view_groups.py",title="群組管理",icon=":material/account_circle:")
case_page=st.Page("view_cases.py",title="案件管理",icon=":material/account_circle:")
photo_page=st.Page("view_photos.py",title="照片管理",icon=":material/camera_alt:")

pg=st.navigation(
    {
        "基本設定":[user_page,group_page,case_page],
        "工作內容":[photo_page]
    }
)

pg.run()