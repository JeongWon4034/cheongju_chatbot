import streamlit as st
from openai import OpenAI
import re

# OpenAI 클라이언트 초기화 (스트림릿 시크릿 키 사용)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 메시지 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """너는 청주 지역 문화유산 전문 관광 가이드야. ... (생략) ..."""
        }
    ]

# 입력 상태 초기화
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("청주 문화 챗봇")

user_input = st.text_input("궁금한 걸 물어보세요!", value=st.session_state.user_input)

if st.button("질문하기"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("답변 작성 중..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.user_input = ""

# 채팅 이력 출력
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"👤 **You**: {msg['content']}")
    else:
        st.markdown(f"🤖 **챗봇**: {msg['content']}")
