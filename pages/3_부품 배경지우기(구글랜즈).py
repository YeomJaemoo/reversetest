import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="이미지 배경 제거", page_icon="😶‍🌫️")

st.write("## 🐧배경을 제거하기")
st.sidebar.write("## 업로드와 다운로드 :gear:")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def fix_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    fixed = remove(image)
    return image, fixed

def main():
    st.title("🤩Google Lens with Streamlit")

    img_file_buffer = st.camera_input("📸사진찍기")
    uploaded_images = st.sidebar.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    session_state = st.session_state

    if "processed_images" not in session_state:
        session_state.processed_images = []
        session_state.last_processed = 0

    new_images = []

    if img_file_buffer is not None:
        image_bytes = img_file_buffer.getvalue()
        if len(image_bytes) > MAX_FILE_SIZE:
            st.error("사진파일이 너무 큽니다. 5MB이하를 업로드하세요.")
        else:
            original_image, fixed_image = fix_image(image_bytes)
            new_images.append((original_image, fixed_image))

    if uploaded_images is not None:
        for upload in uploaded_images[session_state.last_processed:]:
            image_bytes = upload.read()
            if len(image_bytes) > MAX_FILE_SIZE:
                st.error("사진파일이 너무 큽니다. 5MB이하를 업로드하세요.")
            else:
                original_image, fixed_image = fix_image(image_bytes)
                new_images.append((original_image, fixed_image))

    if st.sidebar.button("배경제거 하기 버튼"):
        session_state.processed_images.extend(new_images)
        session_state.last_processed = len(uploaded_images)

    for i, (original_image, fixed_image) in enumerate(session_state.processed_images):
        col1, col2 = st.columns(2)
        col1.write("Original Image :camera:")
        col1.image(original_image)
        col2.write("Fixed Image :wrench:")
        col2.image(fixed_image)
        st.sidebar.download_button(f"배경제거된 이미지 #{i+1}", convert_image(fixed_image), f"fixed_{i+1}.png", "image/png", key=f"download_button_{i}")

    # 초기화 버튼을 추가하여 상태를 리셋하는 기능 추가
    if st.sidebar.button('초기화'):
        session_state.clear()  # 모든 상태 변수 초기화
        st.rerun()  # 새로고침

if __name__ == "__main__":
    main()
