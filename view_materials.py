import streamlit as st
import pandas as pd
import io
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
            try:
                create_material(data)
                st.success("材料新增成功！")
            except Exception as e:
                st.error(f"新增失敗：{e}")
            st.rerun()
    return None

def display_materials(df):
    # 只顯示主要欄位，並用 column_config 中文化
    df_materials = df[['MaterialID', 'Name', 'Unit', 'UnitPrice', 'Content', 'StockQuantity', 'SafetyStock']]
    event = st.dataframe(
        df_materials,
        column_config={
            'MaterialID': '材料ID',
            'Name': '材料名稱',
            'Unit': '單位',
            'UnitPrice': '單價',
            'Content': '說明',
            'StockQuantity': '庫存量',
            'SafetyStock': '安全庫存',
        },
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )

    select_materials = event.selection.rows
    filtered_df = df.iloc[select_materials]

    if filtered_df.empty:
        pass
    else:
        if st.button("🗑️ 刪除材料"):
            from api import delete_material
            for _, row in filtered_df.iterrows():
                try:
                    delete_material(row["MaterialID"])
                except Exception as e:
                    st.error(f"刪除失敗：{e}")
            st.success("材料刪除成功！")
            st.cache_data.clear()
            st.rerun()

        if st.button("🖨️ 輸出QRCODE"):
            from utils_qrcode import generate_qrcode
            #qr_data = f"編碼:{code}|品名:{name}|規格:{spec}|單位:{unit}"
            for _,row in filtered_df.iterrows():

                generate_qrcode(row["MaterialID"], row["Name"], row["Content"], row["Unit"], "./static/qrcode_materials")

            st.toast("QRCODE輸出成功！")


def example_download():
    material_example = pd.DataFrame([
        {
            '材料名稱': '水泥',
            '單位': '包',
            '單價': 150,
            '說明': '灰色水泥',
            '庫存量': 100,
            '安全庫存': 10,
        }
    ])
    excel_buffer = io.BytesIO()
    material_example.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    st.download_button(
        label="📥 下載範例檔",
        data=excel_buffer,
        file_name="material_import_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@st.dialog("🗂️ 匯入材料")
def import_materials():
    uploaded_file = st.file_uploader("請選擇要匯入的Excel檔案", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith("csv"):
                df_import = pd.read_csv(uploaded_file)
            else:
                df_import = pd.read_excel(uploaded_file)
            st.write("### 預覽匯入資料：")
            st.dataframe(df_import)
            if st.button("確認匯入資料", key="import_material_confirm"):
                for row in df_import.to_dict(orient="records"):
                    data = {
                        'Name': row['材料名稱'],
                        'Unit': row['單位'],
                        'UnitPrice': row['單價'],
                        'Content': row['說明'],
                        'StockQuantity': row['庫存量'],
                        'SafetyStock': row['安全庫存']
                    }
                    try:
                        create_material(data)
                    except Exception as e:
                        st.error(f"匯入失敗：{e}")
                st.success("匯入成功！")
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.error(f"匯入失敗：{e}")

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

with st.sidebar:

    st.markdown("#### 材料匯入/範例下載")
    example_download()

    if st.button("🗂️ 匯入材料"):
        import_materials()

    if st.button("🖨️ 全部QRCODE列印"):
        from utils_qrcode import merge_images_to_pdf
        merge_images_to_pdf("./static/qrcode_materials", "./static/qrcode_materials.pdf")
        st.toast("QRCODE列印PDF成功！")