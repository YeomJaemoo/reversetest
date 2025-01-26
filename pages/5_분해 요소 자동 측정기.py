import cv2
import numpy as np
import streamlit as st
from object_detector import *
import base64

# Streamlit 설정
st.set_page_config(
    page_title="분해요소 자동 측정기",
    page_icon="📏"
)

# ArUco 모듈 로드
try:
    import cv2.aruco as aruco
except ImportError:
    st.error("OpenCV에서 ArUco 모듈을 사용할 수 없습니다. 'opencv-contrib-python'이 설치되어 있는지 확인하세요.")
    st.stop()

# ArUco 탐지기 설정
parameters = aruco.DetectorParameters()
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)

# 객체 탐지기 로드
detector = HomogeneousBgDetector()

# Streamlit UI
st.title("📏Measure :red[Object Size]")
st.image('images/Measurement Reference Image.png')
st.write("## 위 이미지를 다운받아 5*5cm로 출력 후 측정할 물체 옆에 두세요!")

# Streamlit 카메라 입력
camera_input = st.camera_input("캡처하려면 카메라를 사용하세요")

if camera_input is not None:
    # 카메라 입력 이미지를 OpenCV 형식으로 변환
    file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # ArUco 마커 탐지
    corners, _, _ = aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:
        # 마커 주위에 다각형 그리기
        int_corners = np.int0(corners)
        cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

        # ArUco 마커 둘레 계산
        aruco_perimeter = cv2.arcLength(corners[0], True)

        # 픽셀 당 cm 비율 계산
        pixel_cm_ratio = aruco_perimeter / 20

        # 객체 탐지
        contours = detector.detect_objects(img)

        # 객체 경계 그리기 및 크기 표시
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            # 객체 너비 및 높이 계산
            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            # 경계 그리기
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.polylines(img, [box], True, (255, 0, 0), 2)

            # 크기 텍스트 표시
            cv2.putText(img, "Width {} cm".format(round(object_width, 1)),
                        (int(x - 100), int(y - 20)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            cv2.putText(img, "Height {} cm".format(round(object_height, 1)),
                        (int(x - 100), int(y + 15)), cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

    # 처리된 이미지 표시
    st.image(img, channels="BGR")

    # 처리된 이미지 다운로드
    if st.button("이미지 다운로드"):
        cv2.imwrite('processed_image.jpg', img)
        with open('processed_image.jpg', "rb") as img_file:
            img_bytes = img_file.read()
        b64_img = base64.b64encode(img_bytes).decode()
        img_href = f'<a href="data:image/jpg;base64,{b64_img}" download="processed_image.jpg">다운로드</a>'
        st.markdown(img_href, unsafe_allow_html=True)
