import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="이미지 배경 제거", page_icon="😶‍🌫️")

st.write("## 🐧 배경을 제거하기")
st.sidebar.write("## 업로드와 다운로드 :gear:")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def fix_image(image_bytes):
    if isinstance(image_bytes, BytesIO):
        image = Image.open(image_bytes)
    else:
        image = Image.open(BytesIO(image_bytes))
    fixed = remove(image)
    return image, fixed

def create_google_lens_url(image_url):
    """
    Google Lens 검색 URL 생성
    """
    base_lens_url = "https://lens.google.com/search?ep=gsbubu&hl=ko&re=df&p="
    return f"{base_lens_url}{image_url}"

# 초기화: 세션 상태에서 필요한 키 설정
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []
if "last_processed" not in st.session_state:
    st.session_state.last_processed = 0

def main():
    st.title("🤩 Google Lens with Streamlit")
    
    # 카메라로 이미지를 입력받거나 파일을 업로드하기
    img_file_buffer = st.camera_input("📸사진찍기")
    uploaded_images = st.sidebar.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    new_images = []

    if img_file_buffer is not None:
        # 카메라로 찍은 이미지를 읽어오기
        image_bytes = img_file_buffer.getvalue()
        if image_bytes is not None:
            if len(image_bytes) > MAX_FILE_SIZE:
                st.error("사진파일이 너무 큽니다. 5MB 이하를 업로드하세요.")
            else:
                original_image, fixed_image = fix_image(image_bytes)
                new_images.append((original_image, fixed_image))

    if uploaded_images is not None:
        # 업로드한 이미지를 읽어오기
        for upload in uploaded_images[st.session_state.last_processed:]:
            image_bytes = upload.read()

            if image_bytes is not None:
                if len(image_bytes) > MAX_FILE_SIZE:
                    st.error("사진파일이 너무 큽니다. 5MB 이하를 업로드하세요.")
                else:
                    original_image, fixed_image = fix_image(image_bytes)
                    new_images.append((original_image, fixed_image))

    if st.sidebar.button("배경제거 하기 버튼"):
        for original_image, fixed_image in new_images:
            # 배경 제거된 이미지를 화면에 표시하여 URL 생성
            fixed_image_display = st.image(fixed_image, use_column_width=True)
            if hasattr(fixed_image_display, "url"):
                fixed_image_url = fixed_image_display.url
                google_lens_url = create_google_lens_url(fixed_image_url)
                st.session_state.processed_images.append((original_image, fixed_image, google_lens_url))

        st.session_state.last_processed += len(new_images)

    for i, (original_image, fixed_image, google_lens_url) in enumerate(st.session_state.processed_images):
        st.write(f"### 이미지 #{i+1}")
        col1, col2 = st.columns(2)
        with col1:
            st.image(original_image, caption="Original Image :camera:", use_column_width=True)
        with col2:
            st.image(fixed_image, caption="Fixed Image :wrench:", use_column_width=True)

        # Google Lens 링크를 이미지 아래 표시
        st.markdown(f"[🔍 Search with Google Lens]({google_lens_url})", unsafe_allow_html=True)
    
    # 초기화 버튼
    if st.sidebar.button('초기화'):
        st.session_state.processed_images = []
        st.session_state.last_processed = 0
        st.rerun()

if __name__ == "__main__":
    main()
