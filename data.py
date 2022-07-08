# -*- coding = utf-8 -*-
# @Time : 2022/7/8 8:56
# @Author : Iscolito
# @File : data.py
# @Software : PyCharm
# -*- coding = utf-8 -*-
# @Time : 2022/7/7 23:29
# @Author : Iscolito
# @File : data.py
# @Software : PyCharm
import pandas as pd
import streamlit as st
import plotly.express as px
import time

#读取基本数据集
df=pd.read_csv("list.csv")
department = df['学校'].unique().tolist()#学校列
number = df['学生人数'].unique().tolist()#人数列
position=[[34.15,109.32]]
for i in range(df.shape[0]):
    position.append([df.values[i,1],df.values[i,2]])

st.markdown('书沁蓝田，情暖校园')
#页眉
st.title('蓝田教育调研数据统计')

#下拉框
st.code('单个学校查询')
st.markdown('(请在左侧下拉框中选择学校)')
product_list = df['学校'].unique()

product_type = st.sidebar.selectbox(
    "请选择学校",
    product_list
)
part_df = df[(df['学校'] == product_type)]
if product_type!='无':
    st.write(part_df)

#数据筛选
number_selection = st.slider('学生人数:',min_value=min(number),max_value=max(number),value=(min(number), max(number)))
st.text('(根据年龄筛选信息拖动数据条，以显示不同条件下的统计图)')
department_selection = st.multiselect('数据选项:',department,default=department)

#年龄分布图
st.header('1.年龄分布图')
mask = (df['学生人数'].between(*number_selection)) & (df['学校'].isin(department_selection))
number_of_result1 = df[mask].shape[0]
st.markdown(f'*有效数据: {number_of_result1}*')
selected={'学校':df[mask]['学校'],'学生人数':df[mask]['学生人数']}
df_grouped1=pd.DataFrame(selected)
bar_chart = px.bar(selected, x='学校',y='学生人数',color_discrete_sequence=['#F63366']*len(df_grouped1),template='plotly_white')
st.plotly_chart(bar_chart)
df_grouped2=pd.DataFrame({'学校':df[mask]['学校'],'学生人数':df[mask]['学生人数'],'基本信息':df[mask]['基本信息']})

# 统计表
st.header('2.统计表')
st.write(df_grouped2)

#地图
st.header('3.地图')
st.text('取决于您的网速，加载可能需要时间')

part_df=pd.DataFrame(
    position,
    columns=['lat', 'lon'])
st.map(part_df)
#进度条显示
latest_iteration = st.empty()
bar = st.progress(0)
for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'当前加载进度 {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)
