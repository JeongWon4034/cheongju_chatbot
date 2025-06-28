import streamlit as st
import openai
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import pandas as pd
from geopy.distance import geodesic

# CSV 불러오기
tour_df = pd.read_csv("cj_tour_place.csv", encoding="cp949")
cafes_df = pd.read_csv("cj_cafe_place.csv", encoding="cp949")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 청주 문화유산 가이드야..."}
    ]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("청주 문화 챗봇")
st.session_state.user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)

if st.button("질문하기"):
    user_input = st.session_state.user_input
    tour_info = []
    mentioned_places = [place for place in tour_df['이름'] if place in user_input]

    if mentioned_places:
        for t_name in mentioned_places:
            t_row = tour_df[tour_df['이름'] == t_name].iloc[0]
            t_desc = f"{t_name}은 청주의 대표 유적지 중 하나입니다."
            t_loc = (t_row['위도'], t_row['경도'])
            cafes_df['거리'] = cafes_df.apply(lambda x: geodesic(t_loc, (x['위도'], x['경도'])).meters, axis=1)
            nearby_cafes = cafes_df.sort_values('거리').head(5)
            cafe_list = "\n".join(nearby_cafes['이름'].astype(str).tolist())
            tour_info.append(f"{t_desc}\n주변 추천 카페 5곳:\n{cafe_list}")
    else:
        sample_places = tour_df.head(3)
        for idx, t_row in sample_places.iterrows():
            t_name = t_row['이름']
            t_desc = f"{t_name}은 청주의 대표 유적지 중 하나입니다."
            tour_info.append(t_desc)

    combined_prompt = f"{user_input}\n\n{chr(10).join(tour_info)}"

    if len(combined_prompt) > 3000:
        combined_prompt = combined_prompt[:3000]

    st.session_state.messages.append({"role": "user", "content": combined_prompt})

    with st.spinner("답변 작성 중..."):
        response = openai.ChatCompletion.create(
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
