import streamlit as st
import api 
import pandas as pd

def calculate_work_hours(df_attendance):

    # 計算每筆打卡的工時
    import altair as alt

    if not df_attendance.empty and 'UserID' in df_attendance.columns and 'ClockInTime' in df_attendance.columns and 'ClockOutTime' in df_attendance.columns:

        user_hours = df_attendance.groupby('UserID')['WorkHours'].sum().reset_index()

        users = api.get_users()
        df_users = pd.DataFrame(users)[['UserID','UserName']]
        user_hours = user_hours.merge(df_users, left_on='UserID', right_on='UserID', how='left')

        user_hours = user_hours.sort_values(by='WorkHours', ascending=False)
        user_hours.columns = ['UserID', '總工時', '人員姓名']
        st.markdown("#### 👷‍♂️ 各人員貢獻總工時")
        # Altair 橫向柱狀圖（顯示中文姓名）
        chart = alt.Chart(user_hours).mark_bar().encode(
            x=alt.X('總工時:Q', title='總工時(小時)'),
            y=alt.Y('人員姓名:N', sort='-x', title='人員'),
            tooltip=['人員姓名', '總工時']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("查無工時資料或資料欄位不完整")

def calculate_cost(df_material_logs):
    # 返回總成本和處理過的DataFrame
    material_cost_total = 0
    processed_df = None
    
    materials = api.get_materials()
    df_materials = pd.DataFrame(materials)[['MaterialID', 'Name', 'UnitPrice']]

    # 合併材料名稱與單價
    if not df_material_logs.empty and 'MaterialID' in df_material_logs.columns:
        df_material_logs = df_material_logs.merge(df_materials, on='MaterialID', how='left')
        # 計算消耗成本
        df_material_logs['ConsumeCost'] = df_material_logs['Quantity_Out'] * df_material_logs['UnitPrice']
        material_cost_total = df_material_logs['ConsumeCost'].sum()

        if 'Name' in df_material_logs.columns and 'ConsumeCost' in df_material_logs.columns:
            import altair as alt
            material_cost = df_material_logs.groupby('Name')['ConsumeCost'].sum().reset_index()
            material_cost = material_cost.sort_values(by='ConsumeCost', ascending=False)
            st.markdown("#### 🧱 材料消耗成本統計")
            # 改為橫向柱狀圖
            chart = alt.Chart(material_cost).mark_bar().encode(
                y=alt.Y('Name:N', sort='-x', title='材料名稱'),
                x=alt.X('ConsumeCost:Q', title='消耗總成本'),
                tooltip=['Name', 'ConsumeCost']
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
            processed_df = df_material_logs
        else:
            st.info("查無材料名稱或消耗成本欄位")
    else:
        st.info("查無材料消耗紀錄或缺少MaterialID欄位")
        
    return material_cost_total, processed_df


@st.cache_data
def get_df_cases():
    case=api.get_cases()
    df_case=pd.DataFrame(case)
    return df_case

@st.cache_data
def get_df_attendance(select_case_id):
    attendance=api.get_attendance_by_case_id(select_case_id)
    df_attendance=pd.DataFrame(attendance)
    return df_attendance

@st.cache_data
def get_df_material_logs(select_case_id):
    material_logs=api.get_material_logs_by_case_id(select_case_id)
    df_material_logs=pd.DataFrame(material_logs)
    return df_material_logs

st.markdown("### 📊儀錶板")

#取得案件

df_case=get_df_cases()

select_case=st.selectbox("案件",options=df_case["Name"])
select_case_id=df_case[df_case["Name"]==select_case]["CaseID"].values[0]
# st.write(select_case_id)
#取得案件出勤紀錄

df_attendance=get_df_attendance(select_case_id)
# st.write(df_attendance)

if df_attendance.empty == False :
    df_attendance['ClockInTime'] = pd.to_datetime(df_attendance['ClockInTime'])
    df_attendance['ClockOutTime'] = pd.to_datetime(df_attendance['ClockOutTime'])
    df_attendance['WorkHours'] = (df_attendance['ClockOutTime'] - df_attendance['ClockInTime']).dt.total_seconds() / 3600
    df_attendance['WorkHours'] = df_attendance['WorkHours'].fillna(0).clip(lower=0)

#取得案件材料用量

df_material_logs=get_df_material_logs(select_case_id)

# 計算材料成本並返回處理過的DataFrame
# METRIC
col1, col2, col3, col4 = st.columns([1,1,1,1], gap="medium",border=True)
col5, col6 = st.columns([1,1],border=True)
with col6:
    material_cost_total, processed_material_logs = calculate_cost(df_material_logs)
with col5:
    calculate_work_hours(df_attendance)

# 人力成本
labor_cost = 0
work_hours = 0
if not df_attendance.empty and 'WorkHours' in df_attendance.columns:
  work_hours = df_attendance['WorkHours'].sum()
  labor_cost = work_hours * 200
#   st.write(work_hours)

# 機具成本（預留）
equipment_cost = None  # 若有資料再補上

# 總成本
sum_cost = material_cost_total + labor_cost

with col1:
  st.metric("材料成本", f"{material_cost_total:,.0f}")
with col2:
  st.metric("人力成本", f"{labor_cost:,.0f}")
with col3:
  st.metric("機具成本", "-")
with col4:
  st.metric("總成本", f"{sum_cost:,.0f}")
