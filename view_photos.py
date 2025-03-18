import streamlit as st
import pandas as pd
from api import get_photos

PHOTOS_FOLDER="D:/backend_yeh_data/photos/"

PAGE_ITEMS = 12
COLUMNS=3

@st.cache_data
def get_photos_df(show_df=False):
    photos=get_photos()
    df= pd.DataFrame(photos)
    if show_df:
        with st.expander("Dataframe"):
            st.dataframe(df, hide_index=True)
    return df

def grid_view(df, page_number, items_per_page=PAGE_ITEMS):
    start_idx = page_number * items_per_page
    end_idx = start_idx + items_per_page
    page_df = df.iloc[start_idx:end_idx]
    
    cols = st.columns(COLUMNS)
    for index, row in page_df.iterrows():
        with cols[index % COLUMNS]:
            single_card(row)

def single_card(row):
    with st.container(border=True):
        st.image(PHOTOS_FOLDER+row["FilePath"],caption="照片編號 :  "+str(row["PhotoID"]))

def get_current_page(df):
    
    with st.sidebar.container(border=True):

        total_items = len(df)

        if total_items==0:
            return -1

        total_pages = (total_items + PAGE_ITEMS - 1) // PAGE_ITEMS  # 向上取整
        current_page= st.number_input("頁次", min_value=1, max_value=total_pages, value=1) - 1
        st.write(f"總共 {total_items} 張照片，第 {current_page + 1} 頁，共 {total_pages} 頁")
        return current_page

def filter_photos(df):
    with st.sidebar.container(border=True):
        filter_type = st.selectbox("篩選類型", ["CaseID", "UserID", "GroupID", "Status"])
        filter_value = st.text_input("輸入篩選值")

        if not filter_value:
            return df

        filtered_df = df[df[filter_type] == filter_value]
        return filtered_df

#########################

st.subheader(" 📸 照片清單")

df = get_photos_df(True)
df_filtered = filter_photos(df)

current_page= get_current_page(df_filtered)

if current_page==-1:
    st.warning("目前沒有照片!")
else:
    grid_view(df_filtered, current_page)

