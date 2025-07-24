import streamlit as st
import pandas as pd
import io
from api import (
    get_equipments,
    create_equipment,
    update_equipment,
    delete_equipment
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

@st.dialog("編輯下次保養日")
def update_equipment_form(equipment):

    import datetime

    st.write(f"機具名稱: **{equipment['Name']}**")
    # st.write(f"目前下次保養日: **{equipment['NextMaintenance'] if pd.notna(equipment['NextMaintenance']) else '未設定'}**")
    
    # 預設為今天
    next_maintenance = st.date_input("下次保養日", value=datetime.date.today())
    
    if st.button("更新"):
        try:
            # 調用 API 更新保養日
            update_equipment(
                equipment_id=equipment['EquipmentID'],
                data={"NextMaintenance": str(next_maintenance)}
            )
            
            st.success(f"已更新 {equipment['Name']} 的下次保養日為 {next_maintenance}")
            st.rerun()
        except Exception as e:
            st.error(f"更新失敗: {str(e)}")
    
    # if st.button("取消"):
    #     st.rerun()

def display_equipments(df):
    
    ## change columns order
    df_equipments = df[['EquipmentID', 'Name','Unit', 'Value', 'Lifespan', 'PurchaseDate', 'NextMaintenance', 'Status']]


    event = st.dataframe(
        df_equipments,
        column_config={
            'EquipmentID': '機具ID',
            'Name': '設備名稱',
            'Unit': '單位',
            'Value': '價值',
            'Lifespan': '耐用年限',
            'PurchaseDate': '購置日期',
            'NextMaintenance': '下次保養日',
            'Status': '狀態'
        },
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )

    select_equipments = event.selection.rows
    filtered_df = df.iloc[select_equipments]

    if filtered_df.empty:
        pass
    else:
        if st.button("🗑️ 刪除機具"):
            for index, row in filtered_df.iterrows():
                delete_equipment(row["EquipmentID"])
            st.success("機具刪除成功！")
            st.cache_data.clear()
            st.rerun()
        
        if st.button("🖨️ 輸出QRCODE"):
            from utils_qrcode import generate_qrcode
            #qr_data = f"編碼:{code}|品名:{name}|規格:{spec}|單位:{unit}"
            for _,row in filtered_df.iterrows():

                generate_qrcode(row["EquipmentID"], row["Name"],row["Value"], row["Unit"], "./static/qrcode_equipments")

            st.toast("QRCODE輸出成功！")

        #編輯選擇的機具的下次保養日
        if st.button("✏️ 編輯下次保養日"):
            # 只處理選擇的第一個機具
            if len(filtered_df) > 1:
                st.warning("一次只能編輯一個機具的保養日")
            else:
                equipment = filtered_df.iloc[0]
                update_equipment_form(equipment)

def example_download():
    equipment_example = pd.DataFrame([
        {
            '設備名稱': '範例機具',
            '單位': '台',
            '價值': 10000,
            '耐用年限': 5,
            '購置日期': '2023-01-01',
            '下次保養日': '2024-01-01',
            '狀態': '可用',
        }
    ])
    excel_buffer = io.BytesIO()
    equipment_example.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        label="📥 下載範例檔",
        data=excel_buffer,
        file_name="equipment_import_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@st.dialog("🗂️ 匯入機具")
def import_equipments():

    uploaded_file = st.file_uploader("請選擇要匯入的Excel檔案", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith("csv"):
                df_import = pd.read_csv(uploaded_file)
            else:
                df_import = pd.read_excel(uploaded_file)
            st.write("### 預覽匯入資料：")
            st.dataframe(df_import)
            if st.button("確認匯入資料", key="import_equipment_confirm"):
                # 這裡可根據實際API批次匯入需求進行呼叫
                for row in df_import.to_dict(orient="records"):
                    data = {
                        'Name': row['設備名稱'],
                        'Unit': row['單位'],
                        'Value': row['價值'],
                        'Lifespan': row['耐用年限'],
                        'PurchaseDate': str(row['購置日期']),
                        'NextMaintenance': str(row['下次保養日']),
                        'Status': row['狀態']
                    }
                    create_equipment(data)
                st.success("匯入成功！")
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.error(f"匯入失敗：{e}")

equipments=get_equipments()

df_equipments = pd.DataFrame(equipments)

st.markdown("### 🛠️ 機具清單")

if df_equipments.empty:
    st.write("目前沒有機具資料")
else:
    display_equipments(df_equipments)

st.markdown("---")

if st.button("➕ 新增機具"):
    equipment_form()

## SIDEBAR

with st.sidebar:
    
    st.markdown("#### 機具匯入/範例下載")
    example_download()

    if st.button("🗂️ 匯入機具"):
        import_equipments()

    if st.button("🖨️ 全部QRCODE列印"):
        from utils_qrcode import merge_images_to_pdf
        merge_images_to_pdf("./static/qrcode_equipments", "./static/qrcode_equipments.pdf")
        st.toast("QRCODE列印PDF成功！")