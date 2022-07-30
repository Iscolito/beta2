# -*- coding = utf-8 -*-
# @Time : 2022/7/7 23:29
# @Author : Iscolito
# @File : data.py
# @Software : PyCharm
import pandas as pd
import streamlit as st
import plotly.express as px
import time
import glob
from PIL import Image
# PIL库仅支持到python2.7，在python3之后需要下载Pillow库，但是代码仍保持PIL
import requests
import datetime
from pyecharts.charts import *
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import streamlit.components.v1 as components


st.set_page_config(page_title="书沁蓝田，情暖校园",page_icon=":rainbow:",layout="wide",initial_sidebar_state="auto")
# 页眉
st.info('书沁蓝田，情暖校园:heart:')

# 天气
st.session_state.date_time=datetime.datetime.now() + datetime.timedelta(hours=8)
@st.cache(ttl=3600)
def get_city_weather(cityId):
    url='https://h5ctywhr.api.moji.com/weatherDetail'
    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data={"cityId":cityId,"cityType":0}
    r=requests.post(url,headers=headers,json=data)
    result=r.json()

    # today forecast
    forecastToday=dict(
        humidity=f"{result['condition']['humidity']}%",
        temp=f"{result['condition']['temp']}°C",
        realFeel=f"{result['condition']['realFeel']}°C",
        weather=result['condition']['weather'],
        wind=f"{result['condition']['windDir']}{result['condition']['windLevel']}级",
        updateTime=(datetime.datetime.fromtimestamp(result['condition']['updateTime'])+datetime.timedelta(hours=8)).strftime('%H:%M:%S')
    )

    # 24 hours forecast
    forecastHours=[]
    for i in result['forecastHours']['forecastHour']:
        tmp={}
        tmp['PredictTime']=(datetime.datetime.fromtimestamp(i['predictTime'])+datetime.timedelta(hours=8)).strftime('%H:%M')
        tmp['Temperature']=i['temp']
        tmp['Body Temperature']=i['realFeel']
        tmp['Humidity']=i['humidity']
        tmp['Weather']=i['weather']
        tmp['Wind']=f"{i['windDesc']}{i['windLevel']}级"
        forecastHours.append(tmp)
    df_forecastHours=pd.DataFrame(forecastHours).set_index('PredictTime')
    return forecastToday,df_forecastHours

st.markdown(f'### {"蓝田县"} 天气预报')
forecastToday,df_forecastHours=get_city_weather(2182)
col1,col2,col3,col4,col5,col6=st.columns(6)
col1.metric('天气',forecastToday['weather'])
col2.metric('气温',forecastToday['temp'])
col3.metric('体感温度',forecastToday['realFeel'])
col4.metric('湿度',forecastToday['humidity'])
col5.metric('风力',forecastToday['wind'])
col6.metric('上次更新时间',forecastToday['updateTime'])
c1 = (
            Line()
            .add_xaxis(df_forecastHours.index.to_list())
            .add_yaxis('Temperature', df_forecastHours.Temperature.values.tolist())
            .add_yaxis('Body Temperature', df_forecastHours['Body Temperature'].values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="24 Hours Forecast"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
                )
            .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
        )
t = Timeline(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width='1200px'))
t.add_schema(play_interval=10000,is_auto_play=True)
t.add(c1, "24 Hours Forecast")
components.html(t.render_embed(), width=1200, height=520)
with st.expander("24 Hours Forecast Data"):
    st.table(df_forecastHours.style.format({'Temperature':'{}°C','Body Temperature':'{}°C','Humidity':'{}%'}))

# 调研纪实
st.title('支教活动纪实')
days = ['空' ,'第一天', '第二天','第三天','第四天','第五天','第六天','第七天','第八天']
day = st.selectbox(
  "您想查看哪一天的纪实？",
  days,
  index=0
  )
day_number = days.index(day)
source_link = 'D{}/*.jpg'.format(day_number)
image_D1_source = glob.glob(source_link)
if len(image_D1_source)==0:
    st.warning('这一天纪实还未更新~')
image_D1 = []
for i in range(len(image_D1_source)):
    image_D1.append(Image.open(image_D1_source[i]))
    # /*为表示“所有”含义的通配符
    st.image(image_D1[i])
    # clamp为图像夹钳，用于固定像素，但是对于url引用无用


# 教育调研

# 读取基本数据集
df=pd.read_csv("list.csv")
department = df['学校'].unique().tolist()#学校列
number = df['学生人数'].unique().tolist()#人数列
position=[[34.15,109.32]]
for i in range(df.shape[0]):
    position.append([df.values[i,1],df.values[i,2]])


st.title('蓝田教育调研数据统计')

# 下拉框
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

# 数据筛选
number_selection = st.slider('学生人数:',min_value=min(number),max_value=max(number),value=(min(number), max(number)))
st.text('(根据年龄筛选信息拖动数据条，以显示不同条件下的统计图)')
department_selection = st.multiselect('数据选项:',department,default=department)

# 年龄分布图
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

# 地图
st.header('3.地图')
st.code('①在线调用地图，无信息显示')
st.text('取决于您的网速，加载可能需要时间')
part_df = pd.DataFrame(
    position,
    columns=['lat', 'lon'])
st.map(part_df)

# 学校实地考察
st.header('4.学校实地考察')
