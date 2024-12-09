import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="이미지 배경 제거", page_icon="😶‍🌫️")

st.write("## 🐧 배경을 제거하고 Google Lens로 검색하기")
st.sidebar.write("## 업로드와 다운로드 :gear:")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def fix_image(image_bytes):
    """
    원본 이미지를 읽어 배경을 제거합니다.
    """
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
    base_lens_url = "https://lens.google.com/search?p="
    return f"{base_lens_url}{image_url}"

def main():
    st.title("🤩 Google Lens with Streamlit")
    
    # 이미지 업로드 또는 카메라 입력
    img_file_buffer = st.camera_input("📸 사진찍기")
    uploaded_images = st.sidebar.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if img_file_buffer is not None:
        # 카메라로 찍은 이미지를 읽어오기
        image_bytes = img_file_buffer.getvalue()
        if len(image_bytes) > MAX_FILE_SIZE:
            st.error("사진파일이 너무 큽니다. 5MB 이하를 업로드하세요.")
        else:
            original_image, fixed_image = fix_image(image_bytes)
            st.image(original_image, caption="Original Image :camera:", use_container_width=True)
            st.image(fixed_image, caption="Fixed Image :wrench:", use_container_width=True)

    if uploaded_images is not None:
        # 업로드한 이미지를 읽어오기
        for upload in uploaded_images:
            image_bytes = upload.read()
            if len(image_bytes) > MAX_FILE_SIZE:
                st.error("사진파일이 너무 큽니다. 5MB 이하를 업로드하세요.")
            else:
                original_image, fixed_image = fix_image(image_bytes)
                st.image(original_image, caption="Original Image :camera:", use_container_width=True)
                st.image(fixed_image, caption="Fixed Image :wrench:", use_container_width=True)

    # 사용자 입력 필드: 이미지 URL 붙여넣기
    st.write("🔗 **이미지 주소를 복사하여 붙여넣으세요.**")
    copied_url = st.text_input("이미지 링크 붙여넣기", placeholder="https://reversetest.streamlit.app/~/+/media/...")

    # Google Lens 검색 버튼
    if copied_url:
        google_lens_url = create_google_lens_url(copied_url)
        st.markdown(f"[🔍 Search with Google Lens]({google_lens_url})", unsafe_allow_html=True)
        st.success("Google Lens 링크가 생성되었습니다. 위 링크를 클릭하세요.")

if __name__ == "__main__":
    main()
