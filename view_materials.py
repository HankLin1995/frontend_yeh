import streamlit as st
import pandas as pd
import io
import plotly.express as px
from api import (
    get_materials,
    create_material,
    update_material,
    get_material
)

@st.dialog("✏️ 編輯材料")
def edit_material(material_id):
    
    # 取得材料詳細資料
    material = get_material(material_id)
    if not material:
        st.error("找不到指定的材料")
        return None
    
    with st.form(f"edit_material_{material_id}"):
        # 顯示不可編輯的欄位
        # st.text_input("材料編號", value=material_id, disabled=True)
        name = st.text_input('材料名稱', value=material.get('Name', ''))
        unit = st.text_input('單位', value=material.get('Unit', ''))
        unit_price = st.number_input(
            '單價', 
            min_value=0.0, 
            value=float(material.get('UnitPrice', 0)), 
            step=1.0
        )
        content = st.text_area('說明', value=material.get('Content', ''))
        stock_quantity = st.number_input(
            '庫存量', 
            min_value=0, 
            value=int(material.get('StockQuantity', 0))
        )
        safety_stock = st.number_input(
            '安全庫存', 
            min_value=0, 
            value=int(material.get('SafetyStock', 0))
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button('儲存變更', use_container_width=True)
        with col2:
            if st.form_submit_button('取消', type='secondary', use_container_width=True):
                return None
                
        if submitted:
            update_data = {
                'Name': name,
                'Unit': unit,
                'UnitPrice': unit_price,
                'Content': content,
                'StockQuantity': stock_quantity,
                'SafetyStock': safety_stock
            }
            try:
                result = update_material(material_id, update_data)
                st.success("材料更新成功！")
                st.rerun()
                return result
            except Exception as e:
                st.error(f"更新失敗：{e}")
    return None
    
    

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

        col1,col2,col3=st.columns(3)

        with col1:
            if st.button("✏️ 編輯材料",use_container_width=True):
                edit_material(filtered_df.iloc[0]["MaterialID"])

        with col2:
            if st.button("🗑️ 刪除材料",use_container_width=True):
                from api import delete_material
                for _, row in filtered_df.iterrows():
                    try:
                        delete_material(row["MaterialID"])
                    except Exception as e:
                        st.error(f"刪除失敗：{e}")
                st.success("材料刪除成功！")
                st.cache_data.clear()
                st.rerun()

        with col3:
            if st.button("🖨️ 輸出QRCODE",use_container_width=True):
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

tab1,tab2=st.tabs(["材料清單","材料報表"])

with tab1:

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

with tab2:
    st.markdown("### 📊 材料庫存管理報表")
    
    if df_materials.empty:
        st.warning("目前沒有材料資料可供分析")
        st.stop()
    
    # 計算缺口數量
    df_materials['缺口數量'] = df_materials['SafetyStock'] - df_materials['StockQuantity']
    df_materials['缺口數量'] = df_materials['缺口數量'].apply(lambda x: max(x, 0))  # 確保缺口不為負數
    
    # 計算庫存狀態
    df_materials['庫存狀態'] = '充足'  # 綠色
    df_materials.loc[df_materials['StockQuantity'] < df_materials['SafetyStock'] * 1.5, '庫存狀態'] = '接近警戒'  # 黃色
    df_materials.loc[df_materials['StockQuantity'] <= df_materials['SafetyStock'], '庫存狀態'] = '不足'  # 紅色
    
    # 計算庫存安全比率 (當前庫存 / 安全庫存)
    df_materials['安全比率'] = df_materials['StockQuantity'] / df_materials['SafetyStock']
    
    # 計算預計缺口天數（假設每天消耗量為安全庫存的5%）
    daily_consumption_rate = 0.05  # 每天消耗安全庫存的5%
    df_materials['預計缺口天數'] = ((df_materials['StockQuantity'] - df_materials['SafetyStock']) / 
                              (df_materials['SafetyStock'] * daily_consumption_rate)).round().astype(int)
    df_materials['預計缺口天數'] = df_materials['預計缺口天數'].apply(lambda x: max(x, 0))  # 確保不為負數

    # 計算各狀態數量
    status_counts = df_materials['庫存狀態'].value_counts()
    total_materials = len(df_materials)
    shortage_count = status_counts.get('不足', 0)
    warning_count = status_counts.get('接近警戒', 0)
    safe_count = status_counts.get('充足', 0)
    
    col1, col2, col3 = st.columns(3, border=True)

    with col1:
        st.metric(
            "🔴 庫存不足", 
            f"{shortage_count} ",
            delta_color="inverse",
            help="庫存已低於或等於安全庫存"
        )
    with col2:
        st.metric(
            "🟡 接近警戒", 
            f"{warning_count} ",
            delta_color="inverse",
            help="庫存低於安全庫存的1.5倍"
        )
    with col3:
        st.metric(
            "🟢 庫存充足", 
            f"{safe_count} ",
            help="庫存充足，超過安全庫存的1.5倍"
        )
    
    with st.container(border=True):
        st.markdown("### 庫存安全比率")

        # 依安全比率由低到高排序
        df_materials.sort_values(by='安全比率', ascending=True, inplace=True)

        # 使用 plotly 繪製條狀圖
        fig_bar = px.bar(
            df_materials,
            x='Name',
            y='安全比率',
            color='庫存狀態',  # 自動依據庫存狀態分色
            color_discrete_map={
                '不足': 'red',
                '接近警戒': 'orange',
                '充足': 'green'
            },
            # title='材料庫存安全比率',
            labels={'安全比率': '安全比率', 'Name': '材料名稱'}
        )

        # 圖表樣式微調
        fig_bar.update_layout(
            xaxis_title='材料名稱',
            yaxis_title='安全比率',
            xaxis_tickangle=-45,
            height=400
        )

        # 顯示圖表
        st.plotly_chart(fig_bar, use_container_width=True)

    with st.container(border=True):
        #顯示不足或接近警戒的材料清單
        st.markdown("### 警示材料清單")
        df_shortage = df_materials[df_materials['庫存狀態'].isin(['不足', '接近警戒'])]
        st.dataframe(df_shortage,
        column_config={
            "Name": "材料名稱",
            "Unit": "單位",
            "UnitPrice": "單價",
            "Content": "說明",
            "StockQuantity": "庫存量",  
            "SafetyStock": "安全庫存",
            "MaterialID": None,
            "CreateTime":None,
            "缺口數量": "缺口數量",
            "庫存狀態": "庫存狀態",
            "安全比率": None,
            "預計缺口天數":None
        },hide_index=True)
        
