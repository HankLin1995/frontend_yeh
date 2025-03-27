import streamlit as st
import pandas as pd
from api import get_cases, get_groups, create_case, update_case,get_case_by_id

st.subheader(" 🚧 案件清單")

@st.cache_data
def get_cases_df():

    cases=get_cases()
    df= pd.DataFrame(cases)[["CaseID","GroupID", "Name", "Content","Location","CreateTime","Status"]]
    df.columns = ["案件ID","群組編號" ,"案件名稱", "案件內容", "案件地點", "創建時間", "案件狀態"]

    group_info_df=get_groups_df()
    df=pd.merge(df,group_info_df,left_on="群組編號",right_on="群組編號",how="left")

    return df

@st.cache_data
def get_groups_df():

    groups=get_groups()
    df= pd.DataFrame(groups)[["GroupID", "Name"]]
    df.columns = ["群組編號", "群組名稱"]
    return df

def show_case_bygroup(df):
    grouped_df = df.groupby("群組名稱")

    for df_grouped in grouped_df:
        with st.expander(f"🟢 {df_grouped[0]}"):
            # 移除 '群組編號' 這一列
            group_data_without_group_id = df_grouped[1].drop(columns=["群組編號","群組名稱"])
            st.dataframe(group_data_without_group_id, hide_index=True)

def show_case(df):
    df=df.drop(columns=["群組編號"])
    st.dataframe(df,hide_index=True)

@st.dialog("新增案件")
def create_case_ui():
    group_name=st.selectbox("群組", options=get_groups_df()["群組名稱"])
    group_id=get_groups_df()[get_groups_df()["群組名稱"]==group_name]["群組編號"].values[0]
    case_name=st.text_input("案件名稱")
    case_content=st.text_area("案件內容")
    case_location=st.text_input("案件地點")

    if st.button("新增案件", key="create_case"):
        create_case(case_name, group_id, case_location, case_content)
        st.cache_data.clear()
        st.rerun()

@st.dialog("更新案件")
def edit_case_ui():
    case_name=st.selectbox("案件", options=get_cases_df()["案件名稱"])
    case_id=get_cases_df()[get_cases_df()["案件名稱"]==case_name]["案件ID"].values[0]
    case=get_case_by_id(case_id)
    case_name=st.text_input("案件名稱", value=case["Name"])
    case_content=st.text_area("案件內容", value=case["Content"])
    case_location=st.text_input("案件地點", value=case["Location"])
    case_status=st.selectbox("案件狀態", options=["new", "completed"])

    if st.button("更新案件", key="edit_case"):
        update_case(case_id, case_name, case_location, case_content, case_status)
        st.cache_data.clear()
        st.rerun()

############################################

# def select_mode():
#     mode=st.sidebar.radio("顯示模式",["群組","全部"])
#     return mode

df=get_cases_df()

show_case_bygroup(df)

# mode=select_mode()

# if mode=="群組":
    # show_case_bygroup(df)
# elif mode=="全部":
    # show_case(df)

# add case

if st.sidebar.button("新增案件"):
    create_case_ui()

if st.sidebar.button("更新案件"):
    edit_case_ui()