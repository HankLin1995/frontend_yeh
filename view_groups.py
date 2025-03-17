import streamlit as st
import pandas as pd
from api import get_groups

st.subheader(" 👨‍👩‍👦‍👦 群組清單")

@st.cache_data
def get_groups_df():

    groups=get_groups()
    df= pd.DataFrame(groups)[["GroupID", "Name", "CreateTime"]]
    df.columns = ["群組ID", "群組名稱", "創建時間"]
    return df

st.dataframe(get_groups_df(),hide_index=True)