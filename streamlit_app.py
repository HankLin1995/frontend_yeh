import streamlit as st
import pandas as pd
import requests
import os
from api import create_user, get_user

VERSION_NUMBER = "V2.0"

st.set_page_config(page_title=f"均嘉ERP系統{VERSION_NUMBER}", page_icon=":derelict_house_building:", layout="wide")
st.logo("./static/BANNER-removebg-preview.png")

test_mode=False

if test_mode==True:

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    if "user_role" not in st.session_state:
        st.session_state.user_role = "admin"
else:
    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""

# LINE LOGIN

line_client_id =os.getenv("LINE_CLIENT_ID")
line_client_secret =os.getenv("LINE_CLIENT_SECRET")
redirect_uri = os.getenv("LINE_REDIRECT_URL")
line_authorization_base_url = "https://access.line.me/oauth2/v2.1/authorize"
line_token_url = "https://api.line.me/oauth2/v2.1/token"
line_userinfo_url = "https://api.line.me/v2/profile"

def info_content():

    st.subheader("📝 使用說明")

    usage_data = {
        "步驟": ["1", "2", "3", "4", "5", "6", "7"],
        "說明": [
            "在 LINE 群組中設定員工，讓系統識別身份。",
            "點擊 **LINE登入** 按鈕進入主要畫面。",
            "透過 **權限管理** 頁面，管理員可以確認權限是否通過。",
            "在 **契約管理** 頁面可進行契約編輯。",
            "在 **案件管理** 頁面可進行案件新增、編輯和刪除。",
            "LINE 群組中上傳的照片會自動備份。",
            "在 **相片管理** 頁面可進行相片歸檔和封存。"
        ]
    }

    df_usage = pd.DataFrame(usage_data)
    st.dataframe(df_usage,hide_index=True)  # 使用 st.table 顯示使用說明

    st.markdown(" ### :keyboard: LINEBOT關鍵字")

    # LINEBOT關鍵字表格
    keyword_data = {
        "關鍵字": ["設定合約:<合約名稱>", "更新合約:<合約名稱>", "刪除合約:<合約名稱>", "設定用戶:<用戶暱稱>"],
        "說明": [
            "針對LINE群組設定合約",
            "針對LINE群組更新合約",
            "針對LINE群組刪除合約",
            "將使用者ID綁定公司ERP並設定用戶暱稱"
        ]
    }

    df_keyword = pd.DataFrame(keyword_data)
    st.dataframe(df_keyword,hide_index=True)  # 使用 st.table 顯示使用說明

def line_login():

    request_uri = (
        f"{line_authorization_base_url}?response_type=code&client_id={line_client_id}"
        f"&redirect_uri={redirect_uri}&state=random_string&scope=profile%20openid%20email"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f" ### :derelict_house_building: 均嘉ERP系統")
        st.write(" :point_right: 使用前請先至**LINE群組**中進行人員設定")
        st.image(r"./static/LOGO.jpg")

        st.link_button('LINE登入', url=request_uri,use_container_width=True,type='primary')

    with col2:

        info_content()

# Process LINE callback
if 'code' in st.query_params and 'state' in st.query_params:
    code = st.query_params['code']
    state = st.query_params['state']
    
    # Request access token
    url = line_token_url
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': line_client_id,
        'client_secret': line_client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    token_json = response.json()

    if response.status_code == 200:

        access_token = token_json['access_token']

        userinfo_response = requests.get(
            line_userinfo_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        userinfo_json = userinfo_response.json()

        st.session_state.user_id=userinfo_json['userId']
        st.session_state.logged_in = True
        # Store user info in session state

        user=get_user(userinfo_json['userId'])
        # st.write(user)

        if user is None:
            new_user=create_user(userinfo_json['userId'],userinfo_json['displayName'],userinfo_json['pictureUrl'],userinfo_json['displayName'])
            st.session_state.user_role=new_user["Role"]
        else:
            st.session_state.user_role=user["Role"]

# Display login or navigation based on login status
if not st.session_state.logged_in:
    line_login()
else:

    # PAGES

    user_page=st.Page("view_users.py",title="用戶管理",icon=":material/account_circle:")
    group_page=st.Page("view_groups.py",title="群組管理",icon=":material/account_circle:")
    case_page=st.Page("view_cases.py",title="案件管理",icon=":material/account_circle:")
    photo_page=st.Page("view_photos.py",title="照片管理",icon=":material/camera_alt:")
    photo_readonly_page=st.Page("view_photos_readonly.py",title="照片瀏覽",icon=":material/camera_alt:")

    # NAVIGATION

    if st.session_state.user_role=="admin" :

        pg=st.navigation(
            {
                "基本設定":[user_page,group_page,case_page],
                "工作內容":[photo_page,photo_readonly_page]
            }
        )

        pg.run()
    
    elif st.session_state.user_role=="manager":

        pg=st.navigation(
            {
                "基本設定":[group_page,case_page],
                "工作內容":[photo_page]
            }
        ) 

        pg.run()

    elif st.session_state.user_role=="worker":

        pg=st.navigation(
            {
                "工作內容":[photo_readonly_page]
            }
        )

        pg.run()

    elif st.session_state.user_role=="none":
        st.error("請等候管理員開通你的權限!")