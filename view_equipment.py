import streamlit as st
import pandas as pd
from api import (
    get_equipments,
    get_equipment_detail,
    create_equipment,
    update_equipment,
    delete_equipment
)

def equipment_status_label(status):
    mapping = {
        'available': '✅ 可借用',
        'borrowed': '🚚 借出中',
        'maintenance': '🛠️ 維修中',
        'scrapped': '❌ 已報廢',
    }
    return mapping.get(status, status)

def display_equipment_table(equipments, filter_status=None, keyword=None):
    df = pd.DataFrame(equipments)
    if filter_status:
        df = df[df['Status'] == filter_status]
    if keyword:
        df = df[df['Name'].str.contains(keyword, case=False, na=False)]
    if df.empty:
        st.info('查無設備資料')
        return
    status_label_map = {'可用': '✅ 可用', '借出': '🚚 借出', '維修中': '🛠️ 維修中', '已報廢': '❌ 已報廢'}
    df['StatusLabel'] = df['Status'].map(status_label_map)
    st.dataframe(
        df[['Name', 'Unit', 'Value', 'Lifespan', 'PurchaseDate', 'NextMaintenance', 'StatusLabel']],
        column_config={
            'Name': st.column_config.TextColumn('設備名稱'),
            'Unit': st.column_config.TextColumn('單位'),
            'Value': st.column_config.NumberColumn('價值'),
            'Lifespan': st.column_config.NumberColumn('耐用年限'),
            'PurchaseDate': st.column_config.TextColumn('購置日期'),
            'NextMaintenance': st.column_config.TextColumn('下次保養日'),
            'StatusLabel': st.column_config.TextColumn('狀態'),
        },
        hide_index=True,
        selection_mode="single-row"
    )

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
            return data
    return None

def main():
    st.title('機具管理系統')
    st.markdown('---')
    equipments = get_equipments()
    st.subheader('設備總覽')
    col1, col2, col3 = st.columns([2,2,3])
    with col1:
        filter_status = st.selectbox('依狀態篩選', options=['全部', 'available', 'borrowed', 'maintenance', 'scrapped'],
                                    format_func=lambda x: '全部' if x=='全部' else equipment_status_label(x))
        filter_status = None if filter_status == '全部' else filter_status
    with col2:
        keyword = st.text_input('搜尋設備名稱')
    with col3:
        if st.button('➕ 新增設備'):
            st.session_state['show_create'] = True
    display_equipment_table(equipments, filter_status, keyword)
    st.markdown('---')
    # 新增設備
    if st.session_state.get('show_create', False):
        st.subheader('新增設備')
        data = equipment_form(mode='create')
        if data:
            create_equipment(data)
            st.success('設備新增成功！')
            st.session_state['show_create'] = False
            st.rerun()
    # 編輯/刪除設備
    selected_id = st.session_state.get('selected_equipment_id')
    if selected_id:
        equipment = get_equipment_detail(selected_id)
        st.subheader(f"編輯設備：{equipment.get('name')}")
        data = equipment_form(equipment, mode='edit')
        if data:
            update_equipment(selected_id, data)
            st.success('設備更新成功！')
            st.session_state['selected_equipment_id'] = None
            st.rerun()
        if st.button('刪除設備', key='delete_equipment', type='primary'):
            delete_equipment(selected_id)
            st.success('設備已刪除！')
            st.session_state['selected_equipment_id'] = None
            st.rerun()

main()
