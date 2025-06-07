import streamlit as st
import pandas as pd
import calendar
import plotly.graph_objects as go
import numpy as np
from datetime import date

# 創建日曆數據
def create_calendar_grid(year, month):
    # 設置星期一為一週的第一天
    calendar.setfirstweekday(calendar.MONDAY)
    
    # 獲取月份的第一天是星期幾和這個月有幾天
    first_day_weekday, days_in_month = calendar.monthrange(year, month)
    
    # 因為calendar設定了星期一為第一天，星期天會是6，所以需要調整first_day_weekday
    # 將原本的0-6（星期日到星期六）轉換為星期一到星期天的範圍（0-6）
    if first_day_weekday == 6:  # 如果是星期日
        first_day_weekday = 0
    else:
        first_day_weekday += 1
    
    # 創建一個6x7的網格（最多6週，每週7天）
    calendar_grid = np.zeros((6, 7), dtype=int)
    
    # 填充日期
    day = 1
    for week in range(6):
        for weekday in range(7):
            if week == 0 and weekday < first_day_weekday:
                # 第一週中，第一天之前的日期留空
                continue
            if day > days_in_month:
                # 超過這個月的天數後留空
                break
            calendar_grid[week, weekday] = day
            day += 1
    
    return calendar_grid

# 創建日曆視覺化
def create_calendar_visualization(year, month, markedDates):
  # 創建日曆網格
  calendarGrid = create_calendar_grid(year, month)
  
  # 確定今天的日期
  todayDate = date.today()
  isCurrentMonth = (todayDate.year == year and todayDate.month == month)
  today = todayDate.day if isCurrentMonth else -1
  
  # 創建一個新的圖形
  fig = go.Figure()
  
  # 設置顏色方案
  weekdayBgColor = "#ffffff"  # 平日背景色
  weekendBgColor = "#f8f9fa"  # 週末背景色
  todayBgColor = "#e3f2fd"    # 今日背景色
  gridColor = "#dee2e6"       # 格線顏色
  weekdayColor = "#212529"    # 平日文字顏色
  weekendColor = "#212529"    # 週末文字顏色
  eventColor="#FF0000"     # 事件標記顏色（紅色）
  
  # 星期幾的標籤
  weekdays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
  
  # 添加星期列標題背景
  for i in range(7):
    fig.add_shape(
      type="rect",
      x0=i, x1=i+1,
      y0=0, y1=1,
      line=dict(color=gridColor, width=1),
      fillcolor="#c5d9d3",
    )
  
  # 添加日曆網格
  for week in range(calendarGrid.shape[0]):
    for day in range(7):
      dateNum = calendarGrid[week, day]
      isWeekend = day == 0 or day == 6  # 週日或週六
      isToday = dateNum == today
      
      # 計算單元格位置
      x0, x1 = day, day + 1
      y0, y1 = -week, -(week + 1)
      
      if dateNum == 0:
        # 空白日期 - 創建淡化的格子
        fig.add_shape(
          type="rect",
          x0=x0, y0=y0, x1=x1, y1=y1,
          line=dict(color=gridColor, width=0.5),
          fillcolor="#f8f9fa",
          opacity=0.5
        )
        continue
      
      # 確定背景色
      bgColor = todayBgColor if isToday else (weekendBgColor if isWeekend else weekdayBgColor)
      textColor = weekendColor if isWeekend else weekdayColor
      
      # 添加日期方格與明顯框線
      fig.add_shape(
        type="rect",
        x0=x0, y0=y0, x1=x1, y1=y1,
        xref="x", yref="y",
        line=dict(color="#a69d9f", width=0.5),
        # fillcolor=bgColor,
        layer="above"
      )
      
      # 添加日期文字
      fig.add_annotation(
        x=(x0 + x1) / 2,
        y=(y0 + y1) / 2 + 0.1,
        text=str(dateNum),
        showarrow=False,
        font=dict(size=16, color=textColor, family="Arial")
      )
      
      # 如果這個日期需要標記紅點(事件)
      if dateNum in markedDates:

        # fig.add_shape(
        #   type="circle",
        #   x0=x0 + 0.5 - 0.08, 
        #   y0=y0 - 0.8 - 0.08,
        #   x1=x0 + 0.5 + 0.08, 
        #   y1=y0 - 0.8 + 0.08,
        #   line=dict(color=eventColor, width=1),
        #   fillcolor=eventColor,
        # )

        add_hours=markedDates[dateNum]

        if add_hours>0:

          fig.add_annotation(
            x=x0+0.5,
            y=y0-0.8-0.02 ,
            text=f"+{add_hours:.1f}".rstrip('0').rstrip('.'),
            showarrow=False,
            font=dict(size=16, color="red", family="Arial")
          )
    
  # 添加星期幾的標籤
  for i, day in enumerate(weekdays):
    fig.add_annotation(
      x=i + 0.5,
      y=0.5,
      text=day,
      showarrow=False,
      font=dict(size=16, color="#2c3e50", family="Arial, sans-serif", weight="bold")
    )
  
  # 新增月份標題顯示
  months = ["一月", "二月", "三月", "四月", "五月", "六月", 
           "七月", "八月", "九月", "十月", "十一月", "十二月"]
  
  # 設置圖表佈局
  fig.update_layout(
    height=650,
    width=780,
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
      showgrid=False,
      zeroline=False,
      showticklabels=False,
      range=[-0.1, 7.1]
    ),
    yaxis=dict(
      showgrid=False,
      zeroline=False,
      showticklabels=False,
      range=[-6.1, 1.1],
      scaleanchor="x",
      scaleratio=1
    ),
    # shapes=[

    #   # 添加一個漸層陰影效果在日曆連線
    #   dict(
    #     type="rect",
    #     xref="paper", yref="paper",
    #     x0=-0.01, y0=-0.01, x1=1.01, y1=1.01,
    #     line=dict(width=1, color="#dee2e6"),
    #     layer="below",
    #     fillcolor="white",
    #     opacity=1
    #   )
    # ]
  )
  
#   # 創建一個小圖例，顯示紅點事件代表的意義
  # if markedDates:
  #   legendX = 0.5
  #   legendY = -6.5
    
  #   fig.add_shape(
  #     type="circle",
  #     x0=legendX - 0.08,
  #     y0=legendY - 0.08,
  #     x1=legendX + 0.08,
  #     y1=legendY + 0.08,
  #     line=dict(color="#FF0000", width=1),
  #     fillcolor="#FF0000"
  #   )
    
  #   fig.add_annotation(
  #     x=legendX + 0.3,
  #     y=legendY,
  #     text="有事件",
  #     showarrow=False,
  #     font=dict(size=14, color="#212529")
  #   )
  
  return fig

# # 創建日曆視覺化
# fig = create_calendar_visualization(2025, 5, [5, 10, 15, 20, 25])

# # 在Streamlit中顯示
# st.plotly_chart(fig)