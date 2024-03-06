import pandas as pd
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as pex
import seaborn as sb
import streamlit as st
sb.set(style='dark')
plt.style.use('dark_background')

#PERSIAPAN DATAFRAME
# Set index data menjadi format Datetime
def setindex_time(data):
    seriesdata = data.copy()
    seriesdata['Datetime'] = pd.to_datetime(seriesdata['Datetime'])
    seriesdata = seriesdata.set_index('Datetime')
    return seriesdata

# Kalkulasi AQI per polutan, berdasarkan standar AQI oleh World Health Organization
def AQI(data):
    copydata = data.copy()
    copydata['PM2.5'] = copydata['PM2.5']/50*100
    copydata['PM10'] = copydata['PM10']/45*100
    copydata['NO2'] = copydata['NO2']/25*100
    copydata['SO2'] = copydata['SO2']/40*100
    copydata['CO'] = copydata['CO']/4000*100
    return copydata

# Kategori AQI berdasarkan standar
def AQIstandard(data):
    AQI_values = list(data.iloc[:,8])
    status_all = []
    for i in AQI_values:
        if (i >= 0) & (i < 34):
            status = "Very Good"
        elif (i >= 34) and (i < 67):
            status = "Good"
        elif (i >= 67) and (i < 100):
            status = "Fair"
        elif (i >= 100) and (i < 150):
            status = "Poor"
        elif (i >= 150) and (i <= 200):
            status = "Very Poor"
        else:
            status = "Hazardous"
        status_all.append(status)
    return status_all

# Kategori AQI berdasarkan standar - satu nilai
def AQIstandard_value(value):
    if (value >= 0) & (value < 34):
        status = "Very Good"
    elif (value >= 34) and (value < 67):
        status = "Good"        
    elif (value >= 67) and (value < 100):
        status = "Fair"
    elif (value >= 100) and (value < 150):
        status = "Poor"
    elif (value >= 150) and (value <= 200):
        status = "Very Poor"
    else:
        status = "Hazardous"
    return status

# Kalkulasi sudut berdasarkan arah mata angin
def WindDirect(data):
    wd = data['wd']
    angles = []
    for dir in wd:
        if dir == 'N':
            angles.append(0)
        elif dir == 'NNE':
            angles.append(22.5)
        elif dir == 'NE':
            angles.append(45)
        elif dir == 'ENE':
            angles.append(67.5)
        elif dir == 'E':
            angles.append(90)
        elif dir == 'ESE':
            angles.append(112.5)
        elif dir == 'SE':
            angles.append(135)
        elif dir == 'SSE':
            angles.append(157.5)
        elif dir == 'S':
            angles.append(180)
        elif dir == 'SSW':
            angles.append(202.5)
        elif dir == 'SW':
            angles.append(225)
        elif dir == 'WSW':
            angles.append(247.5)
        elif dir == 'W':
            angles.append(270)
        elif dir == 'WNW':
            angles.append(292.5)
        elif dir == 'NW':
            angles.append(315)
        elif dir == 'NNW':
            angles.append(337.5)
    return angles

# Membuat data frame AQI town harian
def create_daily_aqi_df(data, town):
    copydata = data.copy()
    polutant = ['PM2.5','PM10','NO2','SO2','CO']
    aqi_df = AQI(copydata.iloc[:,:8]).groupby(copydata.index.floor('d')).mean()
    aqi_df['Daily AQI value'] = aqi_df[polutant].max(axis=1)
    aqi_df['Main AQI Polutant'] = aqi_df[polutant].idxmax(axis=1)
    aqi_df['Daily AQI status'] = AQIstandard(aqi_df)
    return aqi_df
polutant = ['PM2.5','PM10','NO2','SO2','CO']

# Membuat data frame kecepatan dan arah angin per jam
def create_hourly_wind_df(data, town):
    copydata = data.copy()
    wind_data = pd.DataFrame(copydata.iloc[:,9]).groupby([copydata.index.floor('d'),copydata['wd']]).mean().reset_index()
    wind_data = wind_data.set_index('Datetime')
    wind_data['angle'] = WindDirect(wind_data)
    return wind_data

# Penentuan palet untuk visualisasi
def custom_colors(numbers, maxcol = "#2e77bf", restcol = 'lightgrey'):
    number_max = numbers.max()
    pallete = []
    for item in numbers:
        if item == number_max:
          pallete.append(maxcol)
        else:
          if type(restcol) is list:
            for i in restcol:
              pallete.append(i)
          else:
            pallete.append(restcol)
    return pallete

# Data yang digunakan
aoti_df = setindex_time(pd.read_csv('https://raw.githubusercontent.com/nelumbium-nelumbo/air-quality-dashboard/main/aoti_df.csv'))

#FILTER WAKTU DAN TOWN
# Rentang waktu minimum dan maksimum setiap town adalah sama
# Filter tanggal
min_date = datetime.strptime('2013-03-01','%Y-%m-%d').date()
max_date = datetime.strptime('2017-02-28','%Y-%m-%d').date()

with st.sidebar:
    # Filter start date dan end date dari input
    st.image("pollution_beijing@0.5x.png")
    
    start_date, end_date = st.date_input(
        label = "Time Span",
        min_value = min_date, max_value = max_date,
        value = [min_date, max_date]
    )

town = "Aotizhongxin"

if town == "Aotizhongxin":
    aoti_aqi = create_daily_aqi_df(aoti_df, town)
    aoti_aqi = aoti_aqi.reset_index(inplace=False)
    aoti_aqi['Date'] = aoti_aqi['Datetime'].dt.strftime('%Y-%m-%d')
    aoti_aqi = aoti_aqi.set_index('Datetime')
    main_aqi = aoti_aqi[(aoti_aqi['Date'] >= str(start_date)) & (aoti_aqi['Date'] <= str(end_date))]
    aoti_wind = create_hourly_wind_df(aoti_df, town)
    main_wind = aoti_wind.loc[str(end_date)]


#KOMPONEN VISUAL
st.title('Air Quality Dashboard :cloud:')

st.header("About Air Quality Index (AQI)")
st.write("""Air Quality Index atau AQI is a indicator metric of air quality at a certain place. Based on World Health Organization
        (WHO)'s AQI guidelines, each air pollutant (PM2.5, PM10, NO2, SO2, and CO) has its own safety threshold in 24-hours range
        therefore has its own AQI. Daily AQI taken from worst pollutant AQI measure in 24-hours range (biggest AQI value). AQI classified into 6 statuses: Very Good, Good, Fair, Poor, Very Poor, and Hazardous.""")

with st.expander("AQI statuses and thresholds"):
    st.write(pd.DataFrame({
        'AQI status': ['Very Good', 'Good', 'Fair', 'Poor', 'Very Poor', 'Hazardous'],
        'Threshold values': ['0-34', '34-67', '67-100', '100-150', '150-200', '200+']
    }))

with st.expander("AQI calculation method"):
    st.latex(
        r""" AQI Pollutant = \frac{pollutant concentration}{standard} \times 100"""
    )

st.header('Daily Air Quality Index (AQI) in '+town)
col1_1, col1_2, col1_3 = st.columns(3)
with col1_1:
    avg_aqi = main_aqi.iloc[:,8].mean()
    st.metric("Average AQI", value=round(avg_aqi,2))

with col1_2:
    aqi_status = AQIstandard_value(avg_aqi)
    st.metric("Status", value = aqi_status)

with col1_3:
     main_pol = main_aqi[polutant].mean().sort_values(ascending=False).index[0]
     st.metric("Main Pollutant", value = main_pol)

tab1_1, tab1_2, tab1_3 = st.tabs(["Daily AQI Values", "Measured AQI Statuses", "Measured Pollutant"])

with tab1_1:
    st.subheader("Daily AQI Values")
    fig1, ax1 = plt.subplots(figsize=(80, 50))
    ax1.plot(
        main_aqi.index,
        main_aqi.iloc[:,8],
        marker='o',
        linewidth=8,
        color="#2e77bf",
        label="Daily AQI",)
    ax1.axhline(y=avg_aqi, color="#2e9dff", linestyle="--", linewidth=3, label="Average AQI")
    ax1.tick_params(axis='x', labelsize=50)
    ax1.tick_params(axis='y', labelsize=60)
    ax1.legend(prop={'size': 50})
    st.pyplot(fig1)
    
with tab1_2:
    x_aqis = len(main_aqi.iloc[:,10].value_counts().sort_values(ascending=False).index)
    restcols = ['#95b8bf', '#99b9bf', '#a7c4c9', '#a1bdc2', '#a3bbbf']
    explodelist = [0.1, 0, 0, 0, 0, 0]
    colors = custom_colors(main_aqi.iloc[:,10].value_counts().sort_values(ascending=False), restcol = restcols[:x_aqis])
    st.subheader("Measured AQI Statuses")
    fig2, ax2 = plt.subplots()
    ax2.pie(main_aqi.iloc[:,10].value_counts().sort_values(ascending=False), labels=main_aqi.iloc[:,10].value_counts().sort_values(ascending=False).index,
          autopct='%1.1f%%', colors=colors, explode = explodelist[:x_aqis], textprops={'fontsize': 10})
    st.pyplot(fig2)

with tab1_3:
    colorss = custom_colors(main_aqi[polutant].mean().sort_values(ascending=False))
    st.subheader("Measured Pollutants (based on AQI)")
    fig3, ax3 = plt.subplots(figsize=(40, 20))
    ax3.barh(main_aqi[polutant].mean().sort_values(ascending=False).index, main_aqi[polutant].mean().sort_values(ascending=False), align='center', color=colorss)
    ax3.invert_yaxis()  # labels read top-to-bottom
    ax3.tick_params(axis='y', labelsize=40)
    ax3.tick_params(axis='x', labelsize=30)
    st.pyplot(fig3)


st.header("Last 24-hours Air Quality in "+town)
col2_1, col2_2, col2_3, col2_4 = st.columns(4)
with col2_1:
    last_aqi = main_aqi.iloc[len(main_aqi)-1,8]
    st.metric("Average AQI", value=round(last_aqi,2))

with col2_2:
    aqi_status_last = AQIstandard_value(last_aqi)
    st.metric("Status", value = aqi_status_last)

with col2_3:
     main_pol = main_aqi.iloc[len(main_aqi)-1,9]
     st.metric("Main Pollutant", value = main_pol)

with col2_4:
    wind_dir = main_wind.loc[str(end_date)]
    main_wind_dir = wind_dir[wind_dir['WSPM'].max() == wind_dir['WSPM']]['wd'][0]
    st.metric("Wind Direction", value = main_wind_dir)

tab2_1, tab2_2 = st.tabs(["Measured Pollutants", "Wind Speed & Direction"])
with tab2_1:
    x_polutants = len(main_aqi.iloc[len(main_aqi)-1,:5].sort_values(ascending=False).index)
    explodelist2 = [0.1, 0, 0, 0, 0]
    colorsss = custom_colors(main_aqi.iloc[len(main_aqi)-1,:5].sort_values(ascending=False), restcol = restcols[:x_polutants])
    st.subheader("Measured Pollutants 24-hours (based on AQI)")
    fig4, ax4 = plt.subplots()
    ax4.pie(main_aqi.iloc[len(main_aqi)-1,:5], labels=main_aqi.iloc[len(main_aqi)-1,:5].index,
            autopct='%1.1f%%', colors=colorsss, explode = explodelist2[:x_polutants], textprops={'fontsize': 10})
    st.pyplot(fig4)
    
with tab2_2:
    st.subheader("Wind Speed & Direction")
    fig5 = pex.bar_polar(main_wind.loc[str(end_date)], r="WSPM", theta="angle",
                        color="WSPM", color_continuous_scale=pex.colors.sequential.GnBu
                        )
    fig5.update_layout(
        polar = dict(
            angularaxis = dict(
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
                tickmode="array"
                )
            )
        )
    st.plotly_chart(fig5)
