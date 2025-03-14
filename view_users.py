import streamlit as st
import pandas as pd
from api import get_users, update_user_role

st.subheader(" 👨‍👩‍👦‍👦 使用者清單")

def get_users_df():

    users=get_users()
    df= pd.DataFrame(users)[["UserPic","UserID", "UserName", "NickName", "Role","CreateTime"]]
    df.columns = ["圖片","LINEID", "LINE名稱", "別名", "角色", "創建時間"]
    return df

@st.dialog("👨‍💼 編輯用戶")
def edit_user(select_users):

    df_short=select_users[["LINE名稱","別名","角色"]]

    st.dataframe(df_short,hide_index=True)
    st.markdown("---")

    new_role=st.selectbox("角色",options=["none","worker","manager","admin"],index=["none", "worker", "manager", "admin"].index(df_short.iloc[0]['角色']))

    if st.button("確定"):
        for index, row in select_users.iterrows():
            update_user_role(row["LINEID"], new_role)
        st.rerun()

def table_view(df):

    column_configuration={"圖片": st.column_config.ImageColumn()}

    event=st.dataframe(
        df,
        column_config=column_configuration,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )

    select_users=event.selection.rows

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

        col_left,col_right=st.columns(2)

        with col_right:
            try:
                st.image(row["圖片"])
            except:
                st.image("https://via.placeholder.com/150")

        with col_left:
            st.info(f"{row['LINE名稱']}")
            st.text_input("別名",value=row["別名"])
            st.selectbox(f"角色",key=f"role_{row['LINEID']}",options=["none","worker","manager","admin"],index=["none", "worker", "manager", "admin"].index(row['角色']))

####################

users_df=get_users_df()

table_view(users_df)
# grid_view(users_df)
