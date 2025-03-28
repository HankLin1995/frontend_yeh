import streamlit as st
import pandas as pd
from api import (
    get_photos,
    get_photo_by_id,
    get_cases,
    get_case_by_id,
    patch_photo_status_and_caseid,
    patch_photo_phase,
    get_groups,
    get_users,
    get_user
)
import time

PHOTOS_FOLDER="/app/app/uploads/" #D:/backend_yeh_data/photos/"

STATUS_MAP = {
    "新建": "new",
    "歸檔": "approved",
    "垃圾桶": "rejected"
}

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
def get_groups_df():
    groups=get_groups()
    df= pd.DataFrame(groups)[["GroupID", "Name"]]
    return df

@st.cache_data
def get_users_df():
    users=get_users()
    df= pd.DataFrame(users)[["UserID", "UserName"]]
    return df

@st.cache_data
def get_photos_df(show_df=False):
    photos=get_photos()
    df= pd.DataFrame(photos)

    if not df.empty:

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
    
    # cols = st.columns(COLUMNS,vertical_alignment="top")

    # cnt=0
    # for index, row in page_df.iterrows():
    #     with cols[cnt % COLUMNS]:
    #         single_card(row)

    #     cnt=cnt+1

    for i in range(0, len(page_df), COLUMNS):

        cols = st.columns(COLUMNS, vertical_alignment="center")
        cnt=0
        for index, row in page_df[i:i + COLUMNS].iterrows():
            with cols[cnt]:
                single_card(row)
            cnt=cnt+1

    select_all_ui(page_df)

def single_card(row):
    with st.container(border=True):

        ###### deal with photo #######

        label=""

        if row["Status"]=="new":
            label="🟡"
        elif row["Status"]=="approved":
            label="🟢"
        elif row["Status"]=="rejected":
            label="🔴"

        caption_str =label+ f"編號 : {row['PhotoID']}, 時間: {row['CreateTime']}"

        try:
            st.image(PHOTOS_FOLDER+row["FilePath"],caption=caption_str)
        except Exception as e:
            st.error(f"照片讀取錯誤: {e}")

        ####### deal with phase #######

        origin_phase=row["Phase"]

        # st.write(origin_phase)

        if not pd.isna(origin_phase):
            try:
                new_phase=st.pills("🏷️ 標籤",["材料","施工前","施工中","施工後","會議","其他","未設定"],default=origin_phase,key="p_"+str(row["PhotoID"]))
            except:
                new_phase=st.pills("🏷️ 標籤",["材料","施工前","施工中","施工後","會議","其他","未設定"],key="p_"+str(row["PhotoID"]))
        else:
            new_phase=st.pills("🏷️ 標籤",["材料","施工前","施工中","施工後","會議","其他"],key="p_"+str(row["PhotoID"]))

        if origin_phase!=new_phase:
            patch_photo_phase(row["PhotoID"],row["Status"],new_phase)

            if row["PhotoID"] not in st.session_state.selected_photos:
                st.session_state.selected_photos.append(row["PhotoID"])

        ######## deal with case ########

        col1,col2=st.columns([1,2])

        with col2:
            
            if pd.notna(row["CaseID"]): 
                caseid=row["CaseID"]
                df_cases=get_cases_df()
                case_name=df_cases[df_cases["CaseID"]==caseid]["Name"]
                try:
                    st.success(f"{case_name.values[0]}")
                except:
                    pass
                    # st.error("案件不存在")

            if row["Status"]=="new":
                st.warning("新建照片")
            elif row["Status"]=="rejected":
                st.error("垃圾桶")

        with col1:

            if row["PhotoID"] in st.session_state.selected_photos:
                selected_value=True
            else:
                selected_value=False

            if st.checkbox("**選取照片**",value=selected_value, key=row["PhotoID"]):
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

def get_filter_group(df):
    
    df_groups=get_groups_df()
    group_names = ["全部"] + list(df_groups["Name"])
    filter_group = st.selectbox("💠群組", group_names)

    if filter_group == "全部":
        return None
    else:
        filter_group_id = df_groups[df_groups["Name"] == filter_group]["GroupID"].values[0]
        return filter_group_id

def get_filter_user(df):
    df_users=get_users_df()
    user_names = ["全部"] + list(df_users["UserName"])
    filter_user = st.selectbox("💠用戶", user_names)
    if filter_user == "全部":
        return None
    else:
        filter_user_id = df_users[df_users["UserName"] == filter_user]["UserID"].values[0]
        return filter_user_id

def get_filter_case(df):
    df_cases=get_cases_df()
    case_names = ["全部"] + list(df_cases["Name"])
    filter_case = st.selectbox("💠案件", case_names)
    if filter_case == "全部":
        return None
    else:
        filter_case_id = df_cases[df_cases["Name"] == filter_case]["CaseID"].values[0]
        return filter_case_id

def get_filter_status():

    filter_status = st.selectbox("💠狀態", ["全部"] + list(STATUS_MAP.keys()))
    if filter_status == "全部":
        return None
    filter_status_value = STATUS_MAP[filter_status]
    return filter_status_value


def filter_photos(df):

    with st.sidebar.expander("🎯 篩選照片", expanded=False):

        filter_group = get_filter_group(df)
        filter_user = get_filter_user(df)
        filter_case = get_filter_case(df)
        filter_status = get_filter_status()

        if filter_group:
            df = df[df["GroupID"] == filter_group]

        if filter_user:
            df = df[df["UserID"] == filter_user]

        if filter_case:
            df = df[df["CaseID"] == filter_case]

        if filter_status:
            df = df[df["Status"] == filter_status]
            st.session_state.selected_photos=[]

        return df

        # filter_user = st.selectbox("💠用戶", ["All"] + list(df["UserID"].unique()))
        # if filter_user != "All":
        #     df = df[df["UserID"] == filter_user]

        # filter_case = st.selectbox("💠案件", ["All"] + list(df["CaseID"].unique()))
        # if filter_case != "All":
        #     df = df[df["CaseID"] == filter_case]

        # filter_status = st.pills("💠狀態", ["All"] + list(df["Status"].unique()),default="All")
        # if filter_status != "All":
        #     df = df[df["Status"] == filter_status]
        #     st.session_state.selected_photos=[]

        # return df

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
    status=st.selectbox("照片狀態",STATUS_MAP.keys())
    # case_id=get_case_id()
    case_id=None

    if status=="歸檔":
        case_id=get_case_id()

    if st.button("確認更改", type="primary"):   
        for photo_id in st.session_state.selected_photos:

            origin_photo=get_photo_by_id(photo_id)
            origin_case_id=origin_photo["CaseID"]

            patch_photo_status_and_caseid(photo_id, status, case_id)
            move_case_photo(origin_photo,case_id,origin_case_id)

        st.cache_data.clear()
        st.session_state.selected_photos=[]

        st.rerun()

def move_case_photo(photo, case_id, origin_case_id):

    PHOTOS_FOLDER = "/app/app/uploads/"
    PHOTOS_FOLDER_APPROVED = "/app/app/approved/"

    #photo_path=ID_日期_使用者暱稱_階段.格式
    photo_id=photo["PhotoID"]
    photo_path=photo["FilePath"]
    photo_user_id=photo["UserID"]
    photo_user_name=get_user(photo_user_id)["NickName"]
    photo_phase=photo["Phase"]
    photo_date=photo_path.split("_")[0]
    photo_extension=photo_path.split(".")[1]

    photo_filename=f"{photo_id}_{photo_date}_{photo_user_name}_{photo_phase}.{photo_extension}"

    import os
    import shutil

    if not origin_case_id==None:
        origin_case_name=get_case_by_id(origin_case_id)["Name"]

        # 在旧的案件资料夹中删除照片，先检查是否存在再删除
        if origin_case_name:
            origin_case_folder = os.path.join(PHOTOS_FOLDER_APPROVED, origin_case_name)
            origin_photo_path = os.path.join(origin_case_folder, photo_filename)
            if os.path.exists(origin_photo_path):
                os.remove(origin_photo_path)

    if not case_id==None:
        case_name=get_case_by_id(case_id)["Name"]
        # 在新的案件资料夹中复制照片过去
        if case_name:
            case_folder = os.path.join(PHOTOS_FOLDER_APPROVED, case_name)
            if not os.path.exists(case_folder):
                os.makedirs(case_folder)  # 创建新的案件文件夹
            new_photo_path = os.path.join(case_folder, photo_filename)
            
            # 检查照片文件是否存在，如果不存在则复制
            origin_photo_full_path = os.path.join(PHOTOS_FOLDER, photo_path)
            if not os.path.exists(new_photo_path):
                shutil.copyfile(origin_photo_full_path, new_photo_path)

def select_all_ui(page_df):
    col1,col2=st.columns(2)

    with col1:
        # 全選/取消全選目前顯示頁面
        if st.button("✅ 選取本頁全部",use_container_width=True):
            st.session_state.selected_photos = list(page_df["PhotoID"])
            st.rerun()

    with col2:
        # 取消全選
        if st.button("❌ 取消本頁全部",use_container_width=True):
            st.session_state.selected_photos = []
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

if st.sidebar.button("🔃重新整理"):
    st.cache_data.clear()
    st.rerun()
    