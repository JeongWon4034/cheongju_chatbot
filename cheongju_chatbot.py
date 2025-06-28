import streamlit as st
from openai import OpenAI
import re
import pandas as pd

# OpenAI 클라이언트 초기화 (스트림릿 시크릿 키 사용)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# CSV 데이터 불러오기
data = pd.read_csv("data.csv", encoding="cp949")



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

user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)




##############3

if st.button("질문하기"):
    if user_input:
        reply_text = ""
        for place in data['유적지'].unique():
            if place in user_input:
                reply_text += f"\n첫 번째로 추천드릴 곳은 {place}예요! 유적지 설명은 준비 중이에요~"
                nearby_cafes = data[data['유적지'] == place].head(5)
                reply_text += f"\n\n{place} 주변 추천 카페 Top 5:\n"
                for _, row in nearby_cafes.iterrows():
                    reply_text += f"- {row['카페명']}\n"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": reply_text})

        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            final_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": final_reply})
        st.session_state.user_input = ""
# 채팅 이력 출력
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"👤 **You**: {msg['content']}")
    else:
        st.markdown(f"🤖 **챗봇**: {msg['content']}")
