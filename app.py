import streamlit as st
import requests
from datetime import datetime, timedelta

# 1. API 키 설정 (보안 규칙 준수)
API_KEY = st.secrets["WEATHER_API_KEY"]
BASE_URL = "http://api.weatherapi.com/v1"

# [추가] 한글-영문 도시 매칭 딕셔너리 (주요 도시 및 지역)
KOREA_CITIES = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
    "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
    "경기": "Gyeonggi-do", "수원": "Suwon", "고양": "Goyang", "용인": "Yongin",
    "성남": "Seongnam", "부천": "Bucheon", "화성": "Hwaseong", "안산": "Ansan",
    "안양": "Anyang", "평택": "Pyeongtaek", "시흥": "Siheung", "파주": "Paju",
    "의정부": "Uijeongbu", "김포": "Gimpo", "광명": "Gwangmyeong", "군포": "Gunpo",
    "강원": "Gangwon-do", "춘천": "Chuncheon", "원주": "Wonju", "강릉": "Gangneung",
    "충북": "Chungcheongbuk-do", "청주": "Cheongju", "충주": "Chungju",
    "충남": "Chungcheongnam-do", "천안": "Cheonan", "아산": "Asan", "서산": "Seosan",
    "당진": "Dangjin", "전북": "Jeollabuk-do", "전주": "Jeonju", "익산": "Iksan",
    "군산": "Gunsan", "전남": "Jeollanam-do", "여수": "Yeosu", "순천": "Suncheon",
    "목포": "Mokpo", "경북": "Gyeongsangbuk-do", "포항": "Pohang", "구미": "Gumi",
    "경주": "Gyeongju", "안동": "Andong", "경남": "Gyeongsangnam-do", "창원": "Changwon",
    "김해": "Gimhae", "양산": "Yangsan", "진주": "Jinju", "제주": "Jeju"
}

st.set_page_config(page_title="Global Weather AI", page_icon="🌤️", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }
    .stMetric { background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 전 세계 날씨 & 라이프 가이드")

location_input = st.text_input("도시 이름을 입력하세요 (예: 서울, 아산, London)", placeholder="한글 도시명 가능")

if location_input:
    # 한글 입력 시 딕셔너리에서 영문명 변환, 없으면 입력값 그대로 사용
    query = KOREA_CITIES.get(location_input, location_input)
    
    params = {
        "key": API_KEY,
        "q": query,
        "aqi": "yes",
        "days": 2,
        "lang": "ko"
    }
    
    # API 호출
    response = requests.get(f"{BASE_URL}/forecast.json", params=params)
    res = response.json()
    
    # 데이터 파싱
    current = res['current']
    loc = res['location']
    forecast = res['forecast']['forecastday']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader(f"📍 {loc['name']} ({loc['country']})")
        st.metric("현재 온도", f"{current['temp_c']}°C")
        st.write(f"**상태:** {current['condition']['text']}")
        st.image(f"https:{current['condition']['icon']}")
        
        if current['temp_c'] >= 30:
            st.error("너무 더워요! 🥵")

    with col2:
        st.subheader("💧 상세 정보")
        st.write(f"**습도:** {current['humidity']}%")
        st.write(f"**바람 세기:** {current['wind_kph']} km/h")
        
    with col3:
        st.subheader("🌫️ 대기질 (AQI)")
        aqi = current['air_quality']
        st.write(f"**미세먼지(PM10):** {aqi['pm10']:.1f}")
        st.write(f"**초미세먼지(PM2.5):** {aqi['pm2_5']:.1f}")

    st.divider()

    # --- 6시간 전/후 온도 ---
    st.subheader("⏳ 시간대별 온도 변화 (6시간 전/후)")
    now_hour = datetime.now().hour
    h_col1, h_col2 = st.columns(2)
    
    with h_col1:
        t_minus = datetime.now() - timedelta(hours=6)
        # 6시간 전 데이터 (오늘 리스트에서 추출)
        prev_temp = forecast[0]['hour'][t_minus.hour]['temp_c']
        st.info(f"🕒 6시간 전 ({t_minus.strftime('%H:00')}): {prev_temp}°C")

    with h_col2:
        t_plus = datetime.now() + timedelta(hours=6)
        # 내일로 넘어가는 경우 처리
        d_idx = 0 if t_plus.day == datetime.now().day else 1
        next_temp = forecast[d_idx]['hour'][t_plus.hour]['temp_c']
        st.success(f"🕒 6시간 후 ({t_plus.strftime('%H:00')}): {next_temp}°C")

    st.divider()

    # --- 음식 및 관광지 추천 ---
    st.subheader("🎁 날씨 맞춤 추천")
    weather_text = current['condition']['text']
    temp = current['temp_c']
    
    if "비" in weather_text or "소나기" in weather_text:
        food, place = "파전에 막걸리", "실내 미술관"
    elif temp >= 28:
        food, place = "냉면", "워터파크"
    elif temp <= 5:
        food, place = "따끈한 국밥", "실내 쇼핑몰"
    else:
        food, place = "치킨과 맥주", "근처 공원 산책"

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.write(f"🍴 추천 메뉴: **{food}**")
        st.link_button(f"{loc['name']} {food} 맛집", f"https://www.google.com/maps/search/{loc['name']}+{food}+맛집")
    with r_col2:
        st.write(f"🗺️ 추천 장소: **{place}**")
        st.link_button(f"{loc['name']} 주변 명소", f"https://www.google.com/maps/search/{loc['name']}+{place}")