import streamlit as st
import pandas as pd
from api import (
    get_equipments,
    create_equipment
)

@st.dialog("➕ 新增機具")
def equipment_form(equipment=None, mode='create'):
    import datetime
    default = equipment or {}
    with st.form(f"equipment_form_{mode}"):
        name = st.text_input('設備名稱', value=default.get('Name', ''))
        unit = st.text_input('單位', value=default.get('Unit', ''))
        value = st.number_input('價值', min_value=0, value=default.get('Value', 0))
        lifespan = st.number_input('耐用年限', min_value=0, value=default.get('Lifespan', 0))
        purchase_date = st.date_input('購置日期', value=default.get('PurchaseDate', datetime.date.today()))
        next_maintenance = st.date_input('下次保養日', value=default.get('NextMaintenance', datetime.date.today()))
        status_options = ['可用', '借出', '維修中', '已報廢']
        status = st.selectbox('狀態', status_options, index=status_options.index(default.get('Status', '可用')) if default.get('Status') in status_options else 0)
        submitted = st.form_submit_button('儲存')
        if submitted:
            data = {
                'Name': name,
                'Unit': unit,
                'Value': value,
                'Lifespan': lifespan,
                'PurchaseDate': str(purchase_date),
                'NextMaintenance': str(next_maintenance),
                'Status': status
            }
            
            create_equipment(data)
            st.success("機具新增成功！")
            st.rerun()
    return None

def display_equipments(df):
    
    ## change columns order
    df_equipments = df[['EquipmentID', 'Name','Unit', 'Value', 'Lifespan', 'PurchaseDate', 'NextMaintenance', 'Status']]

    ## rename columns
    df_equipments.rename(columns={
        'EquipmentID': '機具ID',
        'Name': '設備名稱',
        'Unit': '單位',
        'Value': '價值',
        'Lifespan': '耐用年限',
        'PurchaseDate': '購置日期',
        'NextMaintenance': '下次保養日',
        'Status': '狀態'
    }, inplace=True)

    st.dataframe(df_equipments, hide_index=True)


equipments=get_equipments()

df_equipments = pd.DataFrame(equipments)

st.markdown("### 🛠️ 機具清單")

display_equipments(df_equipments)

st.markdown("---")

if st.button("➕ 新增機具"):
    equipment_form()

## SIDEBAR

if st.sidebar.button("🗂️匯入檔案"):
    pass
    


