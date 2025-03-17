import streamlit as st
import pandas as pd
from api import get_users, update_user_role

# 定義角色映射字典
ROLE_MAP = {
    "none": "無",
    "worker": "用戶",
    "manager": "管理員",
    "admin": "超級管理員"
}

# 反向映射字典，用於選擇時的處理
ROLE_MAP_REVERSE = {v: k for k, v in ROLE_MAP.items()}

st.subheader(" 👨‍👩‍👦‍👦 使用者清單")

@st.cache_data
def get_users_df():
    users = get_users()
    df = pd.DataFrame(users)[["UserPic", "UserID", "UserName", "NickName", "Role", "CreateTime"]]
    df.columns = ["圖片", "LINEID", "LINE名稱", "別名", "角色", "創建時間"]

    # 映射角色名稱
    df["角色"] = df["角色"].map(ROLE_MAP)
    return df

@st.dialog("👨‍💼 編輯用戶")
def edit_user(select_users):
    df_short = select_users[["LINE名稱", "別名", "角色"]]
    st.dataframe(df_short, hide_index=True)
    st.markdown("---")

    # 根據角色映射選擇
    new_role = st.selectbox("角色", options=list(ROLE_MAP.values()), index=list(ROLE_MAP.values()).index(df_short.iloc[0]['角色']))

    if st.button("確定"):
        new_role_internal = ROLE_MAP_REVERSE[new_role]  # 使用內部角色名更新
        for index, row in select_users.iterrows():
            update_user_role(row["LINEID"], new_role_internal)
        st.cache_data.clear()
        st.rerun()

def table_view(df):
    column_configuration = {"圖片": st.column_config.ImageColumn()}

    event = st.dataframe(
        df,
        column_config=column_configuration,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )

    select_users = event.selection.rows
    filtered_df = df.iloc[select_users]

    if filtered_df.empty:
        pass
    else:
        if st.button("編輯用戶"):
            edit_user(filtered_df)

def grid_view(df):
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            single_card(row)

def single_card(row):
    with st.container(border=True):
        col_left, col_right = st.columns(2)

        with col_right:
            try:
                st.image(row["圖片"])
            except:
                st.image("https://via.placeholder.com/150")

        with col_left:
            st.info(f"{row['LINE名稱']}")
            st.text_input("別名", value=row["別名"])
            st.selectbox(f"角色", key=f"role_{row['LINEID']}", options=list(ROLE_MAP.values()), index=list(ROLE_MAP.values()).index(row['角色']))

####################

# 獲取用戶資料並顯示表格
users_df = get_users_df()

table_view(users_df)
# grid_view(users_df)
