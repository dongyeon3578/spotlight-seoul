import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Spot-Light 안전지도", layout="wide")
st.title("💡 Spot-Light: 서울시 야간 교통사고 사각지대 분석")

# 데이터 로드 (캐시 제거하여 즉시 반영)
@st.cache_data(ttl=0)
def load_data():
    return pd.read_csv('spotlight_real_data.csv')

try:
    df = load_data()
except:
    st.error("데이터 파일을 불러올 수 없습니다.")
    st.stop()

# 통계 기준 설정
acc_75 = df['사고건수'].quantile(0.75)
sl_50 = df['가로등수'].quantile(0.50)

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📊 구역 상세 분석")
    sorted_areas = sorted(df['드롭다운이름'].tolist())
    selected_area = st.selectbox("분석할 구역 선택:", sorted_areas)
    area_info = df[df['드롭다운이름'] == selected_area].iloc[0]
    
    st.metric("가로등 수", f"{int(area_info['가로등수'])}개")
    st.metric("사고 건수", f"{int(area_info['사고건수'])}건")

with col1:
    st.subheader("🗺️ 사각지대 탐색 지도")
    
    # 🌟 지도가 회색으로 나오는 것을 방지하기 위해 좌표 안전장치 추가
    map_lat = area_info['lat'] if not pd.isna(area_info['lat']) else 37.5665
    map_lon = area_info['lon'] if not pd.isna(area_info['lon']) else 126.9780
    
    # 사용자님이 좋아하시던 선명한 지도로 설정
    m = folium.Map(location=[map_lat, map_lon], zoom_start=15, tiles='OpenStreetMap')
    
    for _, row in df.iterrows():
        # 위험도에 따른 색상 결정
        color = 'red' if (row['사고건수'] >= acc_75 and row['가로등수'] < sl_50) else 'blue'
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.6,
            tooltip=row['드롭다운이름']
        ).add_to(m)
    
    # 현재 선택 지역 강조 핀
    folium.Marker([map_lat, map_lon], icon=folium.Icon(color='black', icon='star')).add_to(m)
    
    st_folium(m, width=700, height=500)