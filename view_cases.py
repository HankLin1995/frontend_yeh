import streamlit as st
import pandas as pd
from api import get_cases, get_groups

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
