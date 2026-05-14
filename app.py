import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 웹사이트 기본 설정
st.set_page_config(page_title="Spot-Light 안전지도", layout="wide")
st.title("💡 Spot-Light: 서울시 야간 교통사고 사각지대 분석 시스템")
st.markdown("가로등 밀집도와 교통사고 데이터를 결합하여 **최적의 안전 시설물 입지**를 제안합니다.")

# 2. 전처리 완료된 진짜 서울시 분석 데이터 불러오기
try:
    df = pd.read_csv('spotlight_real_data.csv')
except FileNotFoundError:
    st.error("🚨 데이터 파일을 찾을 수 없습니다. 'spotlight_real_data.csv' 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 3. 분위수(Percentile) 기준점 계산
acc_75 = df['사고건수'].quantile(0.75) 
acc_50 = df['사고건수'].quantile(0.50) 
sl_50 = df['가로등수'].quantile(0.50)  

# 4. 등급 판별 함수 생성
def get_status(acc, sl):
    if acc >= acc_75 and sl < sl_50:
        return "매우 위험", "red", "🚨 가로등 보완 1순위 최우선 대상 구역입니다."
    elif acc >= acc_75 and sl >= sl_50:
        return "위험", "orange", "⚠️ 사고 빈발 구역 (가로등 외 과속방지턱 등 추가 검토)"
    elif acc >= acc_50 and acc < acc_75 and sl < sl_50:
        return "위험", "orange", "⚠️ 사고 증가 추세 (스마트 보안등 선제 설치 권장)"
    elif acc >= acc_50 and acc < acc_75 and sl >= sl_50:
        return "보통", "blue", "🟡 인프라 양호 (지속적 모니터링 필요)"
    else:
        return "안전", "green", "✅ 사고 발생 하위 50% 안전 구역"

# 데이터프레임에 색상 미리 저장
df['color'] = df.apply(lambda row: get_status(row['사고건수'], row['가로등수'])[1], axis=1)

# 5. 레이아웃 쪼개기 (왼쪽: 지도, 오른쪽: 상세 분석)
col1, col2 = st.columns([2, 1])

# --- 오른쪽 패널: 분석할 구역 선택 ---
with col2:
    st.subheader("📊 구역 상세 분석")
    
    sorted_areas = sorted(df['드롭다운이름'].tolist())
    selected_area = st.selectbox("분석할 구역 선택 (클릭 후 타자를 쳐서 검색하세요):", sorted_areas)
    
    area_info = df[df['드롭다운이름'] == selected_area].iloc[0]
    
    st.markdown(f"**📍 선택 지역:** {selected_area.split(' (')[0]}")
    
    status, color, message = get_status(area_info['사고건수'], area_info['가로등수'])
    st.metric(label="설치된 가로등 수", value=f"{int(area_info['가로등수'])} 개")
    st.metric(label="야간 교통사고 발생", value=f"{int(area_info['사고건수'])} 건")
    
    st.divider()
    if status == "매우 위험":
        st.error(f"**{status}**")
        st.write(message)
    elif status == "위험":
        st.warning(f"**{status}**")
        st.write(message)
    elif status == "보통":
        st.info(f"**{status}**")
        st.write(message)
    else:
        st.success(f"**{status}**")
        st.write(message)

# --- 왼쪽 패널: 선택된 지역을 중앙에 두고 지도 그리기 ---
with col1:
    st.subheader("🗺️ 사각지대 탐색 지도")
    
    # 🌟 [수정 포인트 1] 화면에 지역이 좀 더 넓게 보이도록 줌 아웃 (14 -> 13)
    m = folium.Map(location=[area_info['lat'], area_info['lon']], zoom_start=13)
    
    for i, row in df.iterrows():
        if row['사고건수'] > 0 or row['color'] == 'red': 
            # 🌟 [수정 포인트 2] 원 크기 공식 축소 및 최대 크기(12) 제한 설정!
            calc_radius = row['사고건수'] * 0.2 + 3 
            final_radius = min(calc_radius, 12) 
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=final_radius,
                color=row['color'],
                fill=True,
                fill_opacity=0.6,
                tooltip=row['드롭다운이름'] 
            ).add_to(m)
    
    # 선택된 구역에 눈에 띄는 파란색 핀(Marker) 꽂기
    folium.Marker(
        location=[area_info['lat'], area_info['lon']],
        popup=selected_area,
        icon=folium.Icon(color='darkblue', icon='info-sign')
    ).add_to(m)
    
    # 화면에 지도 출력
    st_folium(m, width=700, height=500)