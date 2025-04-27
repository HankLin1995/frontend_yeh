import streamlit as st
import pandas as pd
from api import (
    get_materials,
    create_material
)

@st.dialog("➕ 新增材料")
def material_form(material=None, mode='create'):
    import datetime
    default = material or {}
    with st.form(f"material_form_{mode}"):
        name = st.text_input('材料名稱', value=default.get('Name', ''))
        unit = st.text_input('單位', value=default.get('Unit', ''))
        unit_price = st.number_input('單價', min_value=0.0, value=float(default.get('UnitPrice', 0)), step=1.0)
        content = st.text_area('說明', value=default.get('Content', ''))
        stock_quantity = st.number_input('庫存量', min_value=0, value=int(default.get('StockQuantity', 0)))
        safety_stock = st.number_input('安全庫存', min_value=0, value=int(default.get('SafetyStock', 0)))
        submitted = st.form_submit_button('儲存')
        if submitted:
            data = {
                'Name': name,
                'Unit': unit,
                'UnitPrice': unit_price,
                'Content': content,
                'StockQuantity': stock_quantity,
                'SafetyStock': safety_stock
            }
            create_material(data)
            st.success("材料新增成功！")
            st.rerun()
    return None

def display_materials(df):
    # 顯示所有主要欄位
    df_materials = df[['MaterialID', 'Name', 'Unit', 'UnitPrice', 'Content', 'StockQuantity', 'SafetyStock']]
    df_materials.rename(columns={
        'MaterialID': '材料ID',
        'Name': '材料名稱',
        'Unit': '單位',
        'UnitPrice': '單價',
        'Content': '說明',
        'StockQuantity': '庫存量',
        'SafetyStock': '安全庫存',
        'CreateTime': None
    }, inplace=True)
    st.dataframe(df_materials, hide_index=True)

##### MAIN UI #####

materials = get_materials()
df_materials = pd.DataFrame(materials)

st.markdown("### 🧱 材料清單")

if df_materials.empty:
    st.write("目前沒有材料資料")
else:
    display_materials(df_materials)

st.markdown("---")

if st.button("➕ 新增材料"):
    material_form()

##### SIDE BAR #####
if st.sidebar.button("🗂️匯入檔案"):
    pass