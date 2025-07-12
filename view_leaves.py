import streamlit as st
import pandas as pd
from datetime import datetime, date
import pytz
import time
import api
# from api import (
#     create_leave_entitlement,
#     get_leave_entitlement,
#     get_user_leave_entitlements,
#     update_leave_entitlement,
#     auto_calculate_special_leave,
#     get_users,
#     get_employees
# )

taiwan_tz = pytz.timezone('Asia/Taipei')

def leave_management_page():
    """請假管理主頁面"""
    st.title("請假管理")
    
    tab1, tab2 = st.tabs(["年度假別配額", "請假申請審核"])
    
    with tab1:
        leave_entitlement_page()
    
    with tab2:
        leave_approval_page()

def leave_entitlement_page():
    """年度假別配額管理頁面"""
    st.subheader("年度假別配額管理")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container(border=True):
            st.subheader("新增/更新假別配額")
            
            # 選擇員工
            try:
                users = get_users()
                user_options = {user["UserID"]: f"{user.get('UserName', '未知')} ({user['UserID']})" for user in users}
                selected_user_id = st.selectbox(
                    "選擇員工",
                    options=list(user_options.keys()),
                    format_func=lambda x: user_options.get(x, x)
                )
            except Exception as e:
                st.error(f"無法取得員工列表: {str(e)}")
                selected_user_id = None
            
            # 選擇年度
            current_year = datetime.now(taiwan_tz).year
            year = st.number_input("年度", min_value=current_year-5, max_value=current_year+5, value=current_year)
            
            # 輸入假別天數
            annual_special_leave = st.number_input("特別休假天數", min_value=0.0, value=0.0, step=0.5)
            personal_leave = st.number_input("事假天數", min_value=0.0, value=14.0, step=0.5)
            sick_leave = st.number_input("病假天數", min_value=0.0, value=30.0, step=0.5)
            
            # 自動計算特休按鈕
            if st.button("根據年資自動計算特休", use_container_width=True):
                if selected_user_id:
                    try:
                        # 呼叫自動計算特休的 API
                        response = auto_calculate_special_leave(selected_user_id, year)
                        if "EntitlementID" in response:
                            st.success("已自動計算特休天數")
                            # 更新顯示的特休天數
                            annual_special_leave = float(response["AnnualSpecialLeave"])
                        else:
                            st.error("自動計算特休失敗")
                    except Exception as e:
                        st.error(f"自動計算特休失敗: {str(e)}")
                else:
                    st.warning("請先選擇員工")
            
            # 提交按鈕
            if st.button("儲存配額設定", type="primary", use_container_width=True):
                if selected_user_id:
                    # 準備資料
                    entitlement_data = {
                        "UserID": selected_user_id,
                        "Year": int(year),
                        "AnnualSpecialLeave": float(annual_special_leave),
                        "PersonalLeave": float(personal_leave),
                        "SickLeave": float(sick_leave)
                    }
                    
                    try:
                        # 先檢查是否已存在該年度的配額
                        existing_entitlements = get_user_leave_entitlements(selected_user_id, year)
                        
                        if existing_entitlements and len(existing_entitlements) > 0:
                            # 更新現有配額
                            entitlement_id = existing_entitlements[0]["EntitlementID"]
                            update_data = {
                                "AnnualSpecialLeave": float(annual_special_leave),
                                "PersonalLeave": float(personal_leave),
                                "SickLeave": float(sick_leave)
                            }
                            response = update_leave_entitlement(entitlement_id, update_data)
                            st.success(f"已更新 {year} 年度假別配額")
                        else:
                            # 建立新配額
                            response = create_leave_entitlement(entitlement_data)
                            st.success(f"已建立 {year} 年度假別配額")
                    except Exception as e:
                        st.error(f"儲存配額失敗: {str(e)}")
                else:
                    st.warning("請先選擇員工")
    
    with col2:
        with st.container(border=True):
            st.subheader("員工假別配額列表")
            
            # 選擇員工
            try:
                users = get_users()
                user_options = {user["UserID"]: f"{user.get('UserName', '未知')} ({user['UserID']})" for user in users}
                user_options["all"] = "所有員工"
                filter_user_id = st.selectbox(
                    "篩選員工",
                    options=list(user_options.keys()),
                    format_func=lambda x: user_options.get(x, x),
                    key="filter_user"
                )
            except Exception as e:
                st.error(f"無法取得員工列表: {str(e)}")
                filter_user_id = "all"
            
            # 選擇年度
            current_year = datetime.now(taiwan_tz).year
            filter_year = st.number_input("篩選年度", min_value=current_year-5, max_value=current_year+5, value=current_year, key="filter_year")
            
            # 顯示假別配額列表
            try:
                if filter_user_id == "all":
                    # 顯示所有員工的假別配額
                    all_entitlements = []
                    for user in users:
                        user_entitlements = get_user_leave_entitlements(user["UserID"], filter_year)
                        if user_entitlements:
                            for entitlement in user_entitlements:
                                entitlement["UserName"] = user.get("UserName", "未知")
                            all_entitlements.extend(user_entitlements)
                    
                    if all_entitlements:
                        df = pd.DataFrame(all_entitlements)
                        # 格式化顯示
                        df = df[["EntitlementID", "UserID", "UserName", "Year", "AnnualSpecialLeave", "PersonalLeave", "SickLeave", "UpdateTime"]]
                        df.columns = ["配額ID", "員工ID", "員工姓名", "年度", "特別休假", "事假", "病假", "更新時間"]
                        st.dataframe(df, hide_index=True, use_container_width=True)
                    else:
                        st.info(f"{filter_year} 年度尚無假別配額資料")
                else:
                    # 顯示特定員工的假別配額
                    user_entitlements = get_user_leave_entitlements(filter_user_id, filter_year)
                    if user_entitlements:
                        for entitlement in user_entitlements:
                            entitlement["UserName"] = user_options.get(entitlement["UserID"], "未知").split(" ")[0]
                        
                        df = pd.DataFrame(user_entitlements)
                        # 格式化顯示
                        df = df[["EntitlementID", "UserName", "Year", "AnnualSpecialLeave", "PersonalLeave", "SickLeave", "UpdateTime"]]
                        df.columns = ["配額ID", "員工姓名", "年度", "特別休假", "事假", "病假", "更新時間"]
                        st.dataframe(df, hide_index=True, use_container_width=True)
                    else:
                        st.info(f"該員工 {filter_year} 年度尚無假別配額資料")
            except Exception as e:
                st.error(f"無法取得假別配額資料: {str(e)}")

def leave_approval_page():
    """請假申請審核頁面"""
    st.subheader("請假申請審核")
    st.info("此功能尚未實現")
    # 這裡將來會實現請假申請審核功能

###===========MAIN===========###


users=api.get_users()
employees=api.get_employees()

df_users=pd.DataFrame(users)


if st.sidebar.button("新增假別配額"):
    this_year=datetime.now(taiwan_tz).year
    for employee in employees:
        line_id=employee["line_id"]
        res=api.auto_calculate_special_leave(line_id,this_year)
        st.write(res)
    st.rerun()

leaves=api.get_leave_entitlements()
df_leaves=pd.DataFrame(leaves)
df_leaves=pd.merge(df_leaves,df_users,on="UserID",how="left")

df_leaves_show=df_leaves[["Year","EntitlementID","UserID","UserName","AnnualSpecialLeave","PersonalLeave","SickLeave"]]

# emoji
col1,col2=st.columns(2)
with col1:
    st.markdown("### 📊 年度假別配額總表")
with col2:
    year=st.selectbox("年度",options=df_leaves["Year"].unique(),index=df_leaves["Year"].unique().tolist().index(datetime.now(taiwan_tz).year))
st.dataframe(df_leaves_show[df_leaves_show["Year"]==year],hide_index=True,column_config={
    "Year": None,
    "EntitlementID": "配額ID",
    "UserID": None,
    "UserName": "員工姓名",
    "AnnualSpecialLeave": "特別休假",
    "PersonalLeave": "事假",
    "SickLeave": "病假",
})
