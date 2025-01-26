import openai
import streamlit as st
from streamlit_chat import message
import os
import base64
import speech_recognition as sr
import tempfile

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="3_an_electronic_component_helper",
    page_icon="\ud83d\udd7f"
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
            max_tokens=500)
    return result['choices'][0]['message']['content']

# 음성 입력을 처리하여 텍스트로 변환하는 함수
def process_audio_input(audio_file):
    recognizer = sr.Recognizer()
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_file.write(audio_file.getvalue())
            with sr.AudioFile(temp_audio_file.name) as source:
                audio = recognizer.record(source)
                return recognizer.recognize_google(audio, language='ko-KR')
    except sr.UnknownValueError:
        st.warning("음성을 인식하지 못했습니다. 다시 시도해주세요.")
    except sr.RequestError:
        st.warning("음성 인식 서비스에 문제가 있습니다. 다시 시도해주세요.")
    return ""

# 챗봇의 대화 내용을 저장하고 다운로드 링크를 생성하는 함수
def save_and_download_chat(past, generated):
    chat_content = ""

    for user_msg, chatbot_msg in zip(past, generated):
        chat_content += "사용자: " + user_msg + "\n"
        chat_content += "챗봇: " + chatbot_msg + "\n"
        chat_content += "---" + "\n"

    # 대화 내용을 텍스트 파일로 저장하고 다운로드 링크 생성
    b64 = base64.b64encode(chat_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">대화 내용 다운로드</a>'
    st.markdown(href, unsafe_allow_html=True)

# Streamlit UI 구성
st.image('images/ask_me_chatbot3.png')
st.title("\ud83d\udd7fMeasure :red[Electronic Component Helper]")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if st.button('기존 채팅 삭제'):
    st.session_state['generated'] = []
    st.session_state['past'] = []

autocomplete = st.checkbox("예시로 채우기를 통해 프롬프트 잘 활용해볼까?")
example = {
    "prompt": "핸드폰에서 메인보드가 하는 역할을 100자 내외로 말해줘!"
}

with st.form('form', clear_on_submit=True):
    user_input = st.text_input('\ud83d\ude0e전자 부품이 해당 기기에서의 역할은?',
                               value=example["prompt"] if autocomplete else "",
                               key='input')
    submitted = st.form_submit_button('Send')

# 음성 입력 처리
st.audio_input("음성 메시지를 녹음하여 질문하세요.", key="audio_input")
if st.session_state.get("audio_input"):
    user_input = process_audio_input(st.session_state["audio_input"])

if submitted and user_input:
    # 프롬프트 생성 후 챗봇의 답변 생성
    prompt = create_prompt(user_input)
    chatbot_response = generate_response(prompt)

    st.session_state['past'].append(user_input)
    st.session_state["generated"].append(chatbot_response)

if st.session_state['generated']:
    for i in reversed(range(len(st.session_state['generated']))):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

# 대화 내용 저장 버튼
if st.button('대화 내용 저장'):
    save_and_download_chat(st.session_state['past'], st.session_state['generated'])
