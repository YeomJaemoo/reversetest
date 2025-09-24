import openai
import streamlit as st
from streamlit_chat import message
import os
import base64

# 음성 인식을 위한 추가 라이브러리
import speech_recognition as sr
import tempfile

# API 키 설정은 secrets에서 가져오는 것이 좋습니다.
# openai.api_key = st.secrets["OPENAI_API_KEY"] 
# 로컬 테스트를 위해 임시 키를 사용하거나 환경 변수 설정을 권장합니다.
# 이 코드에서는 실제 API 호출 부분이 없으므로 일단 주석 처리합니다.

st.set_page_config(
    page_title="전자 부품 헬퍼",
    page_icon="🧷"
)

# --- 실제 API 호출이 없으므로, 데모를 위한 가짜 함수로 대체 ---
def generate_response(messages):
    with st.spinner("작성 중..."):
        # 실제로는 여기서 openai.ChatCompletion.create를 호출합니다.
        # 이 예제에서는 받은 질문을 그대로 따라하는 응답을 반환합니다.
        user_question = messages[-1]['content']
        return f"'{user_question}'에 대해 답변을 생성하는 중입니다. 저는 스마트폰의 메인보드가 모든 부품을 연결하고 제어하는 핵심적인 역할을 한다고 설명할 수 있습니다."

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

st.image('https://i.imgur.com/your_image_url.png') # 이미지 경로를 URL 또는 로컬 파일 경로로 수정하세요.

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'audio_questions' not in st.session_state:
    st.session_state['audio_questions'] = []
    
# 'input' 키도 초기화해주는 것이 좋습니다.
if 'input' not in st.session_state:
    st.session_state.input = ""

if st.button('기존 체팅 삭제'):
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['audio_questions'] = []
    st.session_state.input = "" # 채팅 삭제 시 입력창도 비우기

with st.sidebar:
    st.header("🎙️누르고 질문 후 ⏹️누르기")
    # st.audio_input은 현재 Streamlit에 내장된 위젯이 아닙니다.
    # 음성 녹음을 위해서는 외부 라이브러리(e.g., streamlit-webrtc)를 사용해야 합니다.
    # 여기서는 파일 업로더로 대체하여 로직을 보여드립니다.
    uploaded_file = st.file_uploader("음성 파일(.wav)을 업로드하세요.", type=['wav'])
    if uploaded_file is not None:
        with st.spinner("음성을 인식하는 중..."):
            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(uploaded_file) as source:
                    audio = recognizer.record(source)
                    recognized_text = recognizer.recognize_google(audio, language="ko-KR")
                st.success(f"인식된 음성: {recognized_text}")
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

# ========================================================== #
# ✨✨✨ 여기가 핵심 수정 부분입니다 ✨✨✨
# 토글 상태에 따라 st.session_state.input 값을 직접 업데이트합니다.
if autocomplete:
    st.session_state.input = example["prompt"]
else:
    # 토글을 껐을 때, 현재 입력창의 내용이 예시와 같다면 비웁니다.
    # 이렇게 하면 사용자가 직접 수정한 내용은 유지됩니다.
    if st.session_state.input == example["prompt"]:
        st.session_state.input = ""
# ========================================================== #


# ---------------- 메인 영역: 텍스트 질문 입력 폼 ------------------
with st.form('form', clear_on_submit=True):
    # 'value' 인자를 제거하고, 'key'를 통해 st.session_state와 연결합니다.
    user_input = st.text_input('😎전자 부품이 해당 기기에서의 역할은?', key='input')
    submitted = st.form_submit_button('Send')

if submitted and user_input:
    prompt = create_prompt(user_input)
    chatbot_response = generate_response(prompt)
    st.balloons()

    st.session_state['past'].append(user_input)
    st.session_state["generated"].append(chatbot_response)
    st.session_state.input = "" # 제출 후 입력창 초기화

elif st.session_state['audio_questions']:
    for question in st.session_state['audio_questions']:
        prompt = create_prompt(question)
        chatbot_response = generate_response(prompt)

        st.session_state['past'].append(question)
        st.session_state["generated"].append(chatbot_response)

    st.session_state['audio_questions'].clear()

# 채팅 메시지 출력
if st.session_state['generated']:
    for i in reversed(range(len(st.session_state['generated']))):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

# 다운로드 기능 (이전과 동일)
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
