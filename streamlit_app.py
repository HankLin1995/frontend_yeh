import streamlit as st

st.set_page_config(page_title="工程管理系統", layout="wide")

user_page=st.Page("view_users.py",title="用戶管理",icon=":material/account_circle:")

pg=st.navigation(
    {
        "基本設定":[user_page]
    }
)

pg.run()