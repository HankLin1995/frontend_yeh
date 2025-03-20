import streamlit as st
import pandas as pd
from api import get_photos,get_cases,patch_photo_status_and_caseid
import time

PHOTOS_FOLDER="D:/backend_yeh_data/photos/"

PAGE_ITEMS = 12
COLUMNS=3

#將選取到的照片存放於session_state
if "selected_photos" not in st.session_state:
    st.session_state.selected_photos = []

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

@st.cache_data
def get_cases_df():
    cases=get_cases()
    df= pd.DataFrame(cases)[["CaseID","GroupID", "Name", "Content","Location","CreateTime","Status"]]
    df.columns = ["CaseID","GroupID" ,"Name", "Content", "Location", "CreateTime", "Status"]
    return df

@st.cache_data
def get_photos_df(show_df=False):
    photos=get_photos()
    df= pd.DataFrame(photos)

    # 處理時間顯示問題(轉換成 YYYY-MM-DD HH:MM:SS)
    df["CreateTime"] = pd.to_datetime(df["CreateTime"])
    df["CreateTime"] = df["CreateTime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    if show_df:
        with st.expander("Dataframe"):
            st.dataframe(df, hide_index=True)
    return df

def grid_view(df, page_number, items_per_page=PAGE_ITEMS):
    start_idx = page_number * items_per_page
    end_idx = start_idx + items_per_page
    page_df = df.iloc[start_idx:end_idx]
    
    cols = st.columns(COLUMNS)

    cnt=0
    for index, row in page_df.iterrows():
        with cols[cnt % COLUMNS]:
            single_card(row)

        cnt=cnt+1

def single_card(row):
    with st.container(border=True):

        if row["Status"]=="new":
            label="🟡"
        elif row["Status"]=="approved":
            label="🟢"
        elif row["Status"]=="rejected":
            label="🔴"

        caption_str =label+ f"編號 : {row['PhotoID']}, 時間: {row['CreateTime']}"

        st.image(PHOTOS_FOLDER+row["FilePath"],caption=caption_str)

        col1,col2=st.columns(2)

        with col2:

            if row["CaseID"] > 0:
                caseid=row["CaseID"]
                df_cases=get_cases_df()
                case_name=df_cases[df_cases["CaseID"]==caseid]["Name"]
                
                st.success(f"{case_name.values[0]}")

            if row["Status"]=="new":
                st.warning("新建照片")
            elif row["Status"]=="rejected":
                st.error("垃圾桶")


        with col1:

            if row["PhotoID"] in st.session_state.selected_photos:
                selected_value=True
            else:
                selected_value=False

            if st.checkbox("選取",value=selected_value, key=row["PhotoID"]):
                if row["PhotoID"] not in st.session_state.selected_photos:
                    st.session_state.selected_photos.append(row["PhotoID"])
            else:
                if row["PhotoID"] in st.session_state.selected_photos:
                    st.session_state.selected_photos.remove(row["PhotoID"])

def get_current_page(df):
    
    with st.sidebar.container(border=True):

        total_items = len(df)

        if total_items==0:
            return -1

        total_pages = (total_items + PAGE_ITEMS - 1) // PAGE_ITEMS  # 向上取整
        current_page= st.number_input("頁次", min_value=1, max_value=total_pages, value=1) - 1
        st.write(f"第 {current_page + 1} 頁/共 {total_pages} 頁")
        return current_page

def filter_photos(df):
    
    with st.sidebar.expander("🎯 篩選照片", expanded=False):

        filter_group = st.selectbox("💠群組", ["All"] + list(df["GroupID"].unique()))
        if filter_group != "All":
            df = df[df["GroupID"] == filter_group]

        filter_user = st.selectbox("💠用戶", ["All"] + list(df["UserID"].unique()))
        if filter_user != "All":
            df = df[df["UserID"] == filter_user]

        filter_case = st.selectbox("💠案件", ["All"] + list(df["CaseID"].unique()))
        if filter_case != "All":
            df = df[df["CaseID"] == filter_case]

        filter_status = st.pills("💠狀態", ["All"] + list(df["Status"].unique()),default="All")
        if filter_status != "All":
            df = df[df["Status"] == filter_status]
            st.session_state.selected_photos=[]

        return df

def get_case_id():
    df_case=get_cases_df()
    case_name=st.selectbox("指定案件",df_case["Name"])
    case_id=df_case[df_case["Name"]==case_name]["CaseID"].values[0]
    return str(case_id)

@st.dialog("📋照片狀態")
def mark_photos():

    import json

    st.write("選中的照片編號:")
    #convert to list and join with comma
    selected_photos_list=[photo_id for photo_id in st.session_state.selected_photos]
    selected_photos_string = ','.join(map(str, selected_photos_list))
    st.info(selected_photos_string)
    status=st.selectbox("照片狀態",["new","approved","rejected"])
    # case_id=get_case_id()
    case_id=None

    if status=="approved":
        case_id=get_case_id()

    if st.button("確認更改", type="primary"):   
        for photo_id in st.session_state.selected_photos:

            patch_photo_status_and_caseid(photo_id, status, case_id)

            # if status=="approved": patch_photo_case(photo_id, case_id)

        st.cache_data.clear()
        st.session_state.selected_photos=[]
        st.rerun()

#########################

st.subheader(" 📸 照片清單")

df = get_photos_df()
df_filtered = filter_photos(df)

current_page=get_current_page(df_filtered)

if current_page==-1:
    st.warning("目前沒有照片!")
else:
    grid_view(df_filtered, current_page)

# st.sidebar.json(st.session_state.selected_photos)

if st.sidebar.button("📝 修正照片狀態"):
    if st.session_state.selected_photos==[]:
        st.sidebar.warning("請選擇照片!")
    else:
        mark_photos()