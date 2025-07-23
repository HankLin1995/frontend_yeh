import streamlit as st
from api import get_cert_expired

tab1,tab2,tab3=st.tabs(["時效控制","工地總覽","案件總覽"])

with tab1:
    #證照到期提醒
    st.markdown("#### :bell: 證照到期提醒")
    st.dataframe(get_cert_expired(),hide_index=True)
    st.divider()
    #機具維護提醒
    st.markdown("#### :bell: 機具維護提醒")
    st.divider()
    # #歸還逾期提醒
    # st.markdown("#### :bell: 借用逾期提醒")
    # st.divider()
    #出勤異常提醒
    st.markdown("#### :bell: 出勤異常提醒")

with tab2:
    st.markdown("#### 🏗️ 工地總覽")
    st.divider()

with tab3:
    st.markdown("#### 📝 案件總覽")
    st.divider()