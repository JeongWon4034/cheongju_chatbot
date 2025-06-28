import streamlit as st
import openai
import os
from geopy.geocoders import Nominatim
import re
import folium
from streamlit_folium import st_folium

import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# 메시지 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 청주 관광 안내 챗봇이야. 질문에 친절하게 답변해줘. 관광지 추천 시 반드시 줄바꿈해서 장소만 말해줘."}
    ]

# 입력 상태 초기화
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("청주 문화 챗봇")

# 입력창 + 버튼
st.session_state.user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)

if st.button("질문하기"):
    user_input = st.session_state.user_input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("답변 작성 중..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.user_input = ""  # 입력 초기화
        st.experimental_rerun()

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

    st.subheader("🗺️ GPT가 추천한 장소 지도")
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
