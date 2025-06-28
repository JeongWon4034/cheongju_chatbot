import streamlit as st
from openai import OpenAI
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import pandas as pd

# CSV 불러오기 (한글 깨짐 방지)
tour_df = pd.read_csv("cj_tour_place.csv", encoding="cp949")
cafes_df = pd.read_csv("cj_cafe_place.csv", encoding="cp949")

client = OpenAI()

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """너는 청주 지역 문화유산 전문 관광 가이드야. 말투는 따뜻하고 친절하게, 마치 여행을 안내하는 가이드처럼 설명해줘.

사용자가 여러 개의 청주 유적지를 입력하면:

1. 각 유적지가 어떤 역사적·문화적 의미를 지니는지 소개해줘.
2. 각 유적지 주변 5개의 가까운 카페를 부가적으로 알려줘 (위치기반).
3. 입력된 유적지들을 이동하기 편한 동선 순서로 정렬해줘.

※ 장소 이름은 줄 바꿔서 명확하게 보여줘.
※ 동선은 리스트 형태로 순서를 매겨서 출력해줘.
※ 위도·경도 정보는 사용자에게 보여주지 마.
"""
        }
    ]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("청주 문화 챗봇")

st.session_state.user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)

if st.button("질문하기"):
    user_input = st.session_state.user_input
    if user_input:
        tour_info = []
        for idx, t_row in tour_df.iterrows():
            t_name = str(t_row['이름']).strip()
            t_desc = f"{t_name}은 청주의 주요 유적지 중 하나입니다."
            t_loc = (t_row['위도'], t_row['경도'])
            cafes_df['거리'] = cafes_df.apply(lambda x: geodesic(t_loc, (x['위도'], x['경도'])).meters, axis=1)
            nearby_cafes = cafes_df.sort_values('거리').head(5)
            cafe_list = "\n".join(nearby_cafes['이름'].astype(str).tolist())
            tour_info.append(f"{t_desc}\n주변 추천 카페 5곳:\n{cafe_list}")

        combined_prompt = f"{user_input}\n\n아래는 청주 주요 유적지 정보와 주변 추천 카페 5곳입니다. 각 유적지를 중심으로 코스를 짜주고 소개해줘. 위도 경도 정보는 말하지 마.\n\n{chr(10).join(tour_info)}"

        st.session_state.messages.append({"role": "user", "content": combined_prompt})

        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})

        st.session_state.user_input = ""

for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"👤 **You**: {msg['content']}")
    else:
        st.markdown(f"🤖 **챗봇**: {msg['content']}")

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
