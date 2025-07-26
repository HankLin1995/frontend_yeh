import streamlit as st
import pandas as pd
import datetime
import calendar
from api import get_cert_expired, get_cases, get_case_statistics, get_equipment_maintenance, get_attendance_by_month

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

tab1, tab2, tab3 = st.tabs(["⏰ 時效控制", "📊 案件總覽","👥 員工總覽"])

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


with tab2:
    
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

with tab3:
    # 薪資統計部分
    
    # 月份選擇器
    current_year = datetime.datetime.now().year
    months = [
        f"{current_year}-{month:02d}" for month in range(1, 13)
    ]
    selected_month = st.selectbox("選擇月份", months, index=datetime.datetime.now().month-1)
    
    try:
        # 取得選定月份的出勤資料
        attendance = get_attendance_by_month(selected_month)
        
        if attendance and 'employees' in attendance:
            # 分析選定月份的天數
            year, month = map(int, selected_month.split('-'))
            _, last_day = calendar.monthrange(year, month)
            days_in_month = list(range(1, last_day + 1))
            
            # 創建日期欄位
            columns = ["姓名/日期"] + [str(day) for day in days_in_month] + ["合計"]
            
            # 創建表格資料
            table_data = []
            
            # 將每位員工的出勤資料轉換為表格格式
            for emp in attendance['employees']:
                row = [emp['name']]  # 第一欄是員工姓名
                
                # 建立日期對應的工時字典
                hours_by_day = {}
                for record in emp['daily_records']:
                    day = int(record['date'].split('-')[2])  # 取出日期中的「日」
                    hours_by_day[day] = record['hours']
                
                # 填充每一天的工時
                for day in days_in_month:
                    hours = hours_by_day.get(day, 0)
                    # 如果工時大於0，顯示工時值，否則顯示空白
                    row.append(hours if hours > 0 else "")
                
                # 最後一欄是總計
                row.append(str(emp['total_hours']))
                
                table_data.append(row)
            
            # 添加合計行
            total_row = ["合計"]
            for day in days_in_month:
                # 計算每一天的工時總和
                day_total = 0
                for emp in table_data:
                    day_index = day  # 日期對應的索引
                    if day_index < len(emp) and emp[day_index] != "":
                        day_total += float(emp[day_index])
                
                total_row.append(day_total if day_total > 0 else "")
            
            # 最後一格是所有員工總工時
            grand_total = sum(float(emp[-1]) for emp in table_data if emp[-1] != "")
            total_row.append(grand_total)
            
            table_data.append(total_row)
            
            # 創建 DataFrame 並顯示
            df = pd.DataFrame(table_data, columns=columns)
            
            # 顯示表格
            st.markdown(f"### {selected_month} 月份員工出勤表")
            st.dataframe(df, hide_index=True, use_container_width=True)
            
            if st.button("列印薪資單",type="primary"):
                pass

            # 顯示摘要統計
            # st.markdown("### 出勤摘要統計")
            
            # summary_data = []
            # for emp in attendance['employees']:
            #     # 計算出勤天數 (工時 > 0 的天數)
            #     work_days = sum(1 for day in emp['daily_records'] if day['hours'] > 0)
                
            #     summary_data.append({
            #         "員工姓名": emp['name'],
            #         "總工時": emp['total_hours'],
            #         "出勤天數": work_days,
            #         "換算天數": emp['days_equivalent']
            #     })
            
            # # 顯示摘要資料
            # df_summary = pd.DataFrame(summary_data)
            # st.dataframe(df_summary, hide_index=True, use_container_width=True)
            
        else:
            st.info(f"{selected_month} 月份沒有出勤資料")
    except Exception as e:
        st.error(f"取得資料時發生錯誤: {str(e)}")


