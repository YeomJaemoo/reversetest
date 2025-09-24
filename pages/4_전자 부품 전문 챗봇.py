import openai
import streamlit as st
from streamlit_chat import message
import os
import base64

# 음성 인식을 위한 추가 라이브러리
import speech_recognition as sr
import tempfile

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="3_an_electronic_component_helper",
    page_icon="🧷"
)

def create_prompt(
    query,
    system_role=f"""You are an expert on electronic components, and you can tell exactly what role electronic components used in a device play in that device. In particular, you can say well what role electronic components used in mobile phones play. It was Yeom Jae-moo, a technical teacher at Kangshin Middle School, who made you.
    """,
    model='gpt-4o-mini',
    stream=True
):
    user_content = f"""User question: "{str(query)}". """

    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_content}
    ]
    return messages

def generate_response(messages):
    with st.spinner("작성 중..."):
        result = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=500
        )
    return result['choices'][0]['message']['content']

st.image('images/ask_me_chatbot3.png')

# 기존 세션 상태 유지
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# 음성 입력을 받은 질문을 임시로 보관할 리스트
if 'audio_questions' not in st.session_state:
    st.session_state['audio_questions'] = []

# 채팅 삭제 시 모든 기록 초기화 (텍스트 + 음성질문 리스트)
if st.button('기존 체팅 삭제'):
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['audio_questions'] = []

# ---------------- 사이드바: 음성 녹음 UI ------------------
with st.sidebar:
    st.header("🎙️누르고 질문 후 ⏹️누르기")
    audio_data = st.audio_input("질문 내용을 음성으로 보내세요.")
    if audio_data is not None:
        with st.spinner("음성을 인식하는 중..."):
            recognizer = sr.Recognizer()
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data.getvalue())
                    with sr.AudioFile(tmp.name) as source:
                        audio = recognizer.record(source)
                        recognized_text = recognizer.recognize_google(audio, language="ko-KR")
                st.success(f"인식된 음성: {recognized_text}")
                # 인식된 텍스트를 세션상 리스트에 저장(후처리)
                st.session_state['audio_questions'].append(recognized_text)
            except sr.UnknownValueError:
                st.warning("음성을 인식할 수 없었습니다.")
            except sr.RequestError:
                st.warning("서버 문제로 음성을 인식할 수 없습니다.")


# 예시 프롬프트 사용 여부
autocomplete = st.toggle("예시로 채우기를 통해 프롬프트 잘 활용해볼까?")
example = {
    "prompt": "핸드폰에서 메인보드가 하는 역할을 100자 내외로 말해줘!"
}

# ---------------- 메인 영역: 텍스트 질문 입력 폼 ------------------
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('😎전자 부품이 해당 기기에서의 역할은?',
                               value=example["prompt"] if autocomplete else "",
                               key='input')
    submitted = st.form_submit_button('Send')

# ---------------- 질문 처리 로직 ------------------

# 1. 텍스트 질문이 우선순위를 가짐
if submitted and user_input:
    # 텍스트 질문만 처리
    prompt = create_prompt(user_input)
    chatbot_response = generate_response(prompt)
    st.balloons()

    # 채팅 세션 업데이트
    st.session_state['past'].append(user_input)
    st.session_state["generated"].append(chatbot_response)

# 2. 텍스트 질문이 없을 경우에만 음성 질문 처리
elif st.session_state['audio_questions']:
    # 음성 녹음이 여러 번 들어왔다면, 순서대로 전부 처리
    # 필요에 따라 한 개만 처리하고 싶으면 for문 대신 한 개만 pop해서 쓰면 됨
    for question in st.session_state['audio_questions']:
        prompt = create_prompt(question)
        chatbot_response = generate_response(prompt)

        st.session_state['past'].append(question)
        st.session_state["generated"].append(chatbot_response)

    # 처리 후 음성 질문 리스트 초기화
    st.session_state['audio_questions'].clear()


# ---------------- 채팅 메시지 출력(과거순서 역순으로) ------------------
if st.session_state['generated']:
    for i in reversed(range(len(st.session_state['generated']))):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

# ---------------- 대화 내용 다운로드 기능 ------------------
def save_and_download_chat(past, generated):
    chat_content = ""
    for user_msg, chatbot_msg in zip(past, generated):
        chat_content += "사용자: " + user_msg + "\n"
        chat_content += "챗봇: " + chatbot_msg + "\n"
        chat_content += "---" + "\n"

    b64 = base64.b64encode(chat_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">대화 내용 다운로드</a>'
    st.markdown(href, unsafe_allow_html=True)

if st.button('챗봇 내용을 저장'):
    save_and_download_chat(st.session_state['past'], st.session_state['generated'])
