import streamlit as st
from openai import OpenAI
import os
from geopy.geocoders import Nominatim
import re
import folium
from streamlit_folium import st_folium
import pandas as pd

client = OpenAI()

import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# 메시지 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
    {
        "role": "system",
        "content": """너는 청주 지역 문화유산 전문 관광 가이드야. 말투는 따뜻하고 친절하게, 마치 여행을 안내하는 가이드처럼 설명해줘.

사용자가 여러 개의 청주 유적지(예: 상당산성, 청남대, 수암골 등)를 입력하면:

1. 각 유적지가 어떤 역사적·문화적 의미를 지니는지 소개해줘.
2. 관광객이 방문할 때 알아두면 좋은 포인트도 함께 알려줘 (예: 풍경, 계절별 특징, 추천 포토스팟 등).
3. 입력된 유적지들을 이동하기 편한 동선 순서로 정렬해줘. (예: 북쪽 → 남쪽, 가까운 순 등)

※ 장소 이름은 줄 바꿔서 명확하게 보여줘.
※ 동선은 리스트 형태로 순서를 매겨서 출력해줘.

예시 말투:
"첫 번째로 추천드릴 곳은 상당산성이에요! 청주의 대표적인 산성으로, 봄철 벚꽃과 함께 걷기 정말 좋아요~"

친근하지만 정확하고 신뢰도 있는 정보를 제공해주는 게 중요해.
"""
    }
]



# 입력 상태 초기화
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("청주 문화 챗봇")

# OpenAI 클라이언트 생성
client = openai.OpenAI()

# 입력창 + 버튼
st.session_state.user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)

if st.button("질문하기"):
    user_input = st.session_state.user_input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.user_input = ""  # 입력 초기화


# 채팅 이력 출력
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"👤 **You**: {msg['content']}")
    else:
        st.markdown(f"🤖 **챗봇**: {msg['content']}")

# 지도에 장소 마커 자동 표시
if st.session_state.messages[-1]["role"] == "assistant":
    reply = st.session_state.messages[-1]["content"]
    place_pattern = [line.strip("-•● ").strip() for line in reply.split('\n') if line.strip()]
    geolocator = Nominatim(user_agent="cheongju_chatbot")

    st.subheader("🗺️ 청주 챗봇이 추천한 장소 지도")
    m = folium.Map(location=[36.642, 127.489], zoom_start=13)
    coords = []

    for place in place_pattern:
        try:
            location = geolocator.geocode("청주 " + place)
            if location:
                latlon = [location.latitude, location.longitude]
                coords.append(latlon)
                folium.Marker(latlon, popup=place, tooltip=place).add_to(m)
        except:
            continue

    if coords:
        folium.PolyLine(coords, color="blue", weight=3).add_to(m)

    st_folium(m, width=700, height=500)
csv 불러오는거 어디다해야돼 맨 앞?