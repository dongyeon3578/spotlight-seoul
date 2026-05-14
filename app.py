import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Spot-Light 안전지도", layout="wide")
st.title("💡 Spot-Light: 서울시 야간 교통사고 사각지대 분석 (최종 완성)")

@st.cache_data(ttl=0)
def load_data():
    return pd.read_csv('spotlight_real_data.csv')

try:
    df = load_data()
except:
    st.error("데이터 파일을 불러올 수 없습니다.")
    st.stop()

# 통계 기준점
acc_75 = df['사고건수'].quantile(0.75)
acc_50 = df['사고건수'].quantile(0.50)
sl_50 = df['가로등수'].quantile(0.50)

# 🌟 예전에 칭찬받았던 그 '4단계 위험도 분석 로직' 완벽 부활!
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

df['상태'], df['color'], df['메시지'] = zip(*df.apply(lambda x: get_status(x['사고건수'], x['가로등수']), axis=1))

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📊 구역 상세 분석")
    selected_area = st.selectbox("분석할 구역 선택:", sorted(df['드롭다운이름'].unique()))
    area_info = df[df['드롭다운이름'] == selected_area].iloc[0]
    
    st.metric("가로등 수", f"{int(area_info['가로등수'])}개")
    st.metric("사고 건수", f"{int(area_info['사고건수'])}건")
    
    # 🌟 선택한 구역의 상태에 따라 예쁜 색상 알림창 띄우기
    status = area_info['상태']
    msg = area_info['메시지']
    
    st.divider()
    if status == "매우 위험": st.error(f"**{status}**\n\n{msg}")
    elif status == "위험": st.warning(f"**{status}**\n\n{msg}")
    elif status == "보통": st.info(f"**{status}**\n\n{msg}")
    else: st.success(f"**{status}**\n\n{msg}")

with col1:
    st.subheader("🗺️ 사각지대 탐색 지도")
    m = folium.Map(location=[area_info['lat'], area_info['lon']], zoom_start=15, tiles='OpenStreetMap')
    
    for _, row in df.iterrows():
        # 🌟 지저분한 파란색/초록색 점들은 숨기고, '위험(빨강/주황)' 지역만 띄워서 깔끔하게!
        # 단, 현재 선택한 구역은 무슨 색이든 무조건 표시되게 설정
        if row['color'] in ['red', 'orange'] or row['드롭다운이름'] == selected_area:
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8, 
                color=row['color'], 
                fill=True, 
                fill_opacity=0.7,
                tooltip=f"{row['드롭다운이름']} ({row['상태']})"
            ).add_to(m)
    
    # 지금 내가 선택한 동네에 별 모양 핀 꽂기
    folium.Marker([area_info['lat'], area_info['lon']], popup=selected_area, icon=folium.Icon(color='black', icon='star')).add_to(m)
    st_folium(m, width=700, height=500)