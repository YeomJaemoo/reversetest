import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_title="이미지 배경 제거 및 Google Lens 검색", page_icon="🔍")

st.write("## 🐧 배경 제거 및 Google Lens 검색")
st.sidebar.write("## 업로드 및 다운로드")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB 제한

def convert_image(img):
    """
    PIL 이미지를 바이트 데이터로 변환
    """
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def fix_image(image_bytes):
    """
    rembg를 사용해 이미지 배경 제거
    """
    image = Image.open(BytesIO(image_bytes))
    fixed = remove(image)
    return image, Image.open(BytesIO(fixed))

def generate_google_lens_url(image_url):
    """
    Google Lens URL 생성
    """
    base_lens_url = "https://www.google.com/searchbyimage?image_url="
    return f"{base_lens_url}{image_url}"

# 메인 함수
def main():
    st.title("🔍 Google Lens with Streamlit")

    # 이미지 업로드
    uploaded_file = st.sidebar.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image_bytes = uploaded_file.read()
        if len(image_bytes) > MAX_FILE_SIZE:
            st.error("파일 크기가 너무 큽니다. 5MB 이하의 파일을 업로드해주세요.")
        else:
            # 원본 이미지 표시
            st.write("### 원본 이미지")
            original_image = Image.open(BytesIO(image_bytes))
            st.image(original_image, caption="업로드된 원본 이미지", use_column_width=True)

            # 배경 제거 버튼
            if st.button("배경 제거"):
                try:
                    original_image, fixed_image = fix_image(image_bytes)
                    st.write("### 배경 제거된 이미지")
                    st.image(fixed_image, caption="배경 제거 완료", use_column_width=True)

                    # Google Lens 검색 URL 생성
                    st.write("### Google Lens 검색")
                    st.write("처리된 이미지를 업로드한 URL을 입력하세요.")
                    image_url_placeholder = st.text_input(
                        "이미지 URL을 입력하세요",
                        placeholder="https://example.com/your-image-url.png"
                    )

                    if st.button("Google Lens 검색 링크 생성"):
                        if image_url_placeholder.startswith("http"):
                            lens_url = generate_google_lens_url(image_url_placeholder)
                            st.markdown(f"[🔗 Google Lens에서 검색하기]({lens_url})", unsafe_allow_html=True)
                        else:
                            st.error("올바른 이미지 URL을 입력하세요.")
                except Exception as e:
                    st.error(f"배경 제거 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
