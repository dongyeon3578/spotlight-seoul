import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Spot-Light 안전지도", layout="wide")
st.title("💡 Spot-Light: 서울시 야간 교통사고 사각지대 분석")

@st.cache_data(ttl=0)
def load_data():
    return pd.read_csv('spotlight_real_data.csv')

df = load_data()
acc_75 = df['사고건수'].quantile(0.75)
sl_50 = df['가로등수'].quantile(0.50)

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📊 구역 상세 분석")
    selected_area = st.selectbox("분석할 구역 선택:", sorted(df['드롭다운이름'].unique()))
    area_info = df[df['드롭다운이름'] == selected_area].iloc[0]
    st.metric("가로등 수", f"{int(area_info['가로등수'])}개")
    st.metric("사고 건수", f"{int(area_info['사고건수'])}건")

with col1:
    st.subheader("🗺️ 사각지대 탐색 지도")
    # 🌟 2번째 사진처럼 선명한 지도를 위해 'OpenStreetMap' 사용 및 줌 설정
    m = folium.Map(location=[area_info['lat'], area_info['lon']], zoom_start=15, tiles='OpenStreetMap')
    
    for _, row in df.iterrows():
        color = 'red' if (row['사고건수'] >= acc_75 and row['가로등수'] < sl_50) else 'blue'
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8, color=color, fill=True, fill_opacity=0.6,
            tooltip=row['드롭다운이름']
        ).add_to(m)
    
    folium.Marker([area_info['lat'], area_info['lon']], icon=folium.Icon(color='black', icon='star')).add_to(m)
    st_folium(m, width=700, height=500)