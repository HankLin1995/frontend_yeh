import streamlit as st
import pandas as pd
import datetime
from api import get_cert_expired, get_cases, get_case_statistics, get_equipment_maintenance

tab1, tab2 = st.tabs(["⏰ 時效控制", "📊 案件總覽"])

with tab1:
    #證照到期提醒
    st.markdown("#### :bell: 證照到期提醒")

    cert_expired=get_cert_expired()
    df_cert_expired=pd.DataFrame(cert_expired)

    df_show=["certificate_name","issue_date","expiry_date","employee_name","days_expired"]

    st.dataframe(df_cert_expired[df_show],hide_index=True,column_config={
        "certificate_name":"證照名稱",
        "issue_date":"發證日",
        "expiry_date":"到期日",
        "employee_name":"員工名稱",
        "days_expired":"超過天數"
    })
    st.divider()
    #機具維護提醒
    st.markdown("#### :bell: 機具維護提醒")
    equipment_maintenance=get_equipment_maintenance()

    df_equipment_maintenance=pd.DataFrame(equipment_maintenance)
    df_show=["EquipmentID","Name","PurchaseDate","NextMaintenance","days_overdue"]
    
    st.dataframe(df_equipment_maintenance[df_show],hide_index=True,column_config={
        "Name":"機具名稱",
        "EquipmentID":"機具ID",
        "PurchaseDate":"購買日期",
        "NextMaintenance":"下次維護日期",
        "days_overdue":"超過天數"
    })
    st.divider()
    # #歸還逾期提醒
    # st.markdown("#### :bell: 借用逾期提醒")
    # st.divider()
    # #出勤異常提醒
    # st.markdown("#### :bell: 出勤異常提醒")


def display_case_overview(case_id):
    """
    顯示特定案件的詳細成本統計
    
    Args:
        case_id: 案件ID
    """
    # 獲取案件統計資料
    case_stats = get_case_statistics(case_id)
    
    # 顯示案件基本資訊
    # st.subheader(f"📊 {case_stats['CaseName']} (ID: {case_stats['CaseID']})")
    
    # 顯示摘要資訊
    col1, col2, col3 = st.columns(3,border=True)
    
    # 材料成本
    material_cost = case_stats['TotalMaterialCost']
    
    # 計算人力成本 (假設每小時人力成本為 250 元)
    hourly_rate = 250  # 每小時人力成本
    labor_cost = case_stats['TotalWorkHours'] * hourly_rate
    
    # 計算總成本
    total_cost = material_cost + labor_cost
    
    with col1:
        st.metric("材料成本", f"${material_cost:,}")
    with col2:
        st.metric("人力成本", f"${labor_cost:,}")
    with col3:
        st.metric("總成本", f"${total_cost:,}")
    
    # 顯示材料成本明細
    st.markdown("#### 📦 材料成本明細")
    if case_stats['Materials']:
        df_materials = pd.DataFrame(case_stats['Materials'])
        st.dataframe(
            df_materials,
            hide_index=True,
            column_config={
                "MaterialID": None,
                "Name": st.column_config.TextColumn("材料名稱"),
                "Unit": st.column_config.TextColumn("單位"),
                "UnitPrice": st.column_config.NumberColumn("單價", format="$%d"),
                "Quantity": st.column_config.NumberColumn("數量"),
                "TotalCost": st.column_config.NumberColumn("總成本", format="$%d"),
            },
            use_container_width=True
        )
    else:
        st.info("此案件尚未使用任何材料")
    
    # 顯示人力工時明細
    st.markdown("#### 👷 人力工時明細")
    if case_stats['Attendances']:
        df_attendances = pd.DataFrame(case_stats['Attendances'])

        # 轉換日期時間格式
        df_attendances['ClockInTime'] = pd.to_datetime(df_attendances['ClockInTime'])
        df_attendances['ClockOutTime'] = pd.to_datetime(df_attendances['ClockOutTime'])
        
        # 添加日期列以便分組
        df_attendances['Date'] = df_attendances['ClockInTime'].dt.date
        
        # 顯示每日工時統計
        daily_hours = df_attendances.groupby('Date')['WorkHours'].sum().reset_index()
        daily_hours['Date'] = daily_hours['Date'].astype(str)
        
        # 顯示每人工時統計及比例
        user_hours = df_attendances.groupby('UserName')['WorkHours'].sum().reset_index()
        total_hours = user_hours['WorkHours'].sum()
        user_hours['Percentage'] = (user_hours['WorkHours'] / total_hours * 100).round(1)
        user_hours = user_hours.sort_values(by='WorkHours', ascending=False)
        
        # 顯示員工工時統計
        st.dataframe(
            user_hours,
            hide_index=True,
            column_config={
                "UserName": st.column_config.TextColumn("員工名稱"),
                "WorkHours": st.column_config.NumberColumn("工時(小時)"),
                "Percentage": st.column_config.ProgressColumn("工時比例", format="%.1f%%", min_value=0, max_value=100),
            },
            use_container_width=True
        )
        
        # 顯示工時圖表
        # st.markdown("#### 每日工時統計")
        # st.bar_chart(daily_hours.set_index('Date'))
        
        # 顯示原始打卡記錄
        # with st.expander("打卡記錄明細"):
        #     df_attendances['ClockInTime'] = df_attendances['ClockInTime'].dt.strftime("%Y-%m-%d %H:%M")
        #     df_attendances['ClockOutTime'] = df_attendances['ClockOutTime'].dt.strftime("%Y-%m-%d %H:%M")
            
        #     st.dataframe(
        #         df_attendances.drop(columns=['Date']),
        #         hide_index=True,
        #         column_config={
        #             "UserID": st.column_config.TextColumn("員工ID"),
        #             "IsTrained": st.column_config.CheckboxColumn("已訓練"),
        #             "ClockInTime": st.column_config.TextColumn("上班時間"),
        #             "ClockOutTime": st.column_config.TextColumn("下班時間"),
        #             "WorkHours": st.column_config.NumberColumn("工時(小時)"),
        #         },
        #         use_container_width=True
        #     )
    else:
        st.info("此案件尚未有打卡記錄")

def display_all_cases_overview():
    """
    顯示所有案件的成本統計摘要
    """
    # 這個函數預留給未來實作
    # 如果 API 端點 /cases/statistics 已實作，可以在這裡顯示所有案件的統計摘要
    st.info("所有案件統計摘要功能開發中...")

with tab2:
    # st.markdown("#### 📝 案件總覽")
    
    # 獲取所有案件
    cases = get_cases()
    
    # 建立案件選擇器
    if cases:
        case_options = [f"{case['Name']} (ID: {case['CaseID']})" for case in cases]
        selected_case = st.selectbox("選擇案件", case_options)
        
        # 解析選擇的案件ID
        selected_case_id = int(selected_case.split("ID: ")[1].replace(")", ""))
        
        # 顯示選擇的案件統計資料
        display_case_overview(selected_case_id)
    else:
        st.warning("目前沒有可用的案件")
    
    st.divider()