import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Spot-Light 안전지도", layout="wide")

# 🌟 업데이트 확인용: 제목에 '최종 완성본' 글자가 추가되었습니다!
st.title("💡 Spot-Light: 서울시 야간 교통사고 사각지대 분석 (최종 완성본 🚀)")
st.markdown("가로등 밀집도와 교통사고 데이터를 결합하여 **최적의 안전 시설물 입지**를 제안합니다.")

# 🌟 핵심: 서버가 예전 데이터를 기억하지 못하도록 1초마다 초기화!
@st.cache_data(ttl=1)
def load_data():
    return pd.read_csv('spotlight_real_data.csv')

try:
    df = load_data()
except FileNotFoundError:
    st.error("🚨 데이터 파일을 찾을 수 없습니다.")
    st.stop()

acc_75 = df['사고건수'].quantile(0.75) 
acc_50 = df['사고건수'].quantile(0.50) 
sl_50 = df['가로등수'].quantile(0.50)  

def get_status(acc, sl):
    if acc >= acc_75 and sl < sl_50:
        return "매우 위험", "red", "🚨 가로등 보완 1순위 최우선 대상 구역입니다."
    elif acc >= acc_75 and sl >= sl_50:
        return "위험", "orange", "⚠️ 사고 빈발 구역 (가로등 외 추가 시설 검토)"
    elif acc >= acc_50 and acc < acc_75 and sl < sl_50:
        return "위험", "orange", "⚠️ 사고 증가 추세 (보안등 선제 설치 권장)"
    elif acc >= acc_50 and acc < acc_75 and sl >= sl_50:
        return "보통", "blue", "🟡 인프라 양호 (지속적 모니터링 필요)"
    else:
        return "안전", "green", "✅ 사고 발생 하위 50% 안전 구역"

df['color'] = df.apply(lambda row: get_status(row['사고건수'], row['가로등수'])[1], axis=1)

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📊 구역 상세 분석")
    sorted_areas = sorted(df['드롭다운이름'].tolist())
    selected_area = st.selectbox("분석할 구역 선택:", sorted_areas)
    
    area_info = df[df['드롭다운이름'] == selected_area].iloc[0]
    st.markdown(f"**📍 선택 지역:** {selected_area}")
    
    status, color, message = get_status(area_info['사고건수'], area_info['가로등수'])
    st.metric(label="설치된 가로등 수", value=f"{int(area_info['가로등수'])} 개")
    st.metric(label="야간 교통사고 발생", value=f"{int(area_info['사고건수'])} 건")
    
    if status == "매우 위험": st.error(f"**{status}**\n\n{message}")
    elif status == "위험": st.warning(f"**{status}**\n\n{message}")
    elif status == "보통": st.info(f"**{status}**\n\n{message}")
    else: st.success(f"**{status}**\n\n{message}")

with col1:
    st.subheader("🗺️ 사각지대 탐색 지도")
    
    # 🌟 사용자님이 원하시던 '예쁜 기본 지도(OpenStreetMap)' 강제 적용!
    m = folium.Map(location=[area_info['lat'], area_info['lon']], zoom_start=14, tiles='OpenStreetMap')
    
    for i, row in df.iterrows():
        if row['사고건수'] > 0 or row['color'] == 'red': 
            # 원 크기가 화면을 가리지 않도록 예쁜 크기로 고정
            final_radius = min(row['사고건수'] * 0.3 + 3, 15) 
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=final_radius,
                color=row['color'],
                fill=True,
                fill_opacity=0.7,
                tooltip=f"{row['드롭다운이름']} (사고 {int(row['사고건수'])}건)"
            ).add_to(m)
    
    folium.Marker(
        location=[area_info['lat'], area_info['lon']],
        popup=selected_area,
        icon=folium.Icon(color='darkblue', icon='info-sign')
    ).add_to(m)
    
    st_folium(m, width=700, height=500)