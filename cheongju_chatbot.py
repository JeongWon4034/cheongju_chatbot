import streamlit as st
from openai import OpenAI
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import pandas as pd

# CSV 불러오기
tour_df = pd.read_csv("cj_tour_place.csv", encoding="cp949")
cafes_df = pd.read_csv("cj_cafe_place.csv", encoding="cp949")

client = OpenAI()
openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 청주 지역 문화유산 전문 관광 가이드야..."}
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
            t_desc = f"{t_name}은 청주의 대표 유적지 중 하나입니다."
            t_loc = (t_row['위도'], t_row['경도'])
            cafes_df['거리'] = cafes_df.apply(lambda x: geodesic(t_loc, (x['위도'], x['경도'])).meters, axis=1)
            nearby_cafes = cafes_df.sort_values('거리').head(5)
            cafe_list = "\n".join(nearby_cafes['이름'].astype(str).tolist())
            tour_info.append(f"{t_desc}\n주변 추천 카페 5곳:\n{cafe_list}")

        combined_prompt = f"{user_input}\n\n아래는 유적지 정보와 주변 카페입니다. 각 유적지를 중심으로 코스를 짜주고 소개해줘. 위도경도 정보는 말하지 마.\n\n{chr(10).join(tour_info)}"
        st.session_state.messages.append({"role": "user", "content": combined_prompt})

        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
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
    geolocator = Nominatim(user_agent="cheongju_chatbot")
    m = folium.Map(location=[36.642, 127.489], zoom_start=13)
    coords = []
    for place in tour_df['이름']:
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
    st.subheader("🗺️ 청주 챗봇 추천 코스 지도")
    st_folium(m, width=700, height=500)
