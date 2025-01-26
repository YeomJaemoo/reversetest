import cv2
import numpy as np
import streamlit as st
from object_detector import *
import base64

st.set_page_config(
    page_title="분해요소 자동 측정기",
    page_icon="📏"
)

# Load Aruco detector
parameters = cv2.aruco.DetectorParameters()
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)

# Load Object Detector
detector = HomogeneousBgDetector()

st.title("📏Measure :red[Object Size]")
st.image('images/Measurement Reference Image.png')
st.write("## 위 이미지를 다운받아 5*5cm로 출력 후 측정할 물체 옆에 두세요!")

# Use Streamlit's camera_input for capturing images
camera_input = st.camera_input("캡처하려면 카메라를 사용하세요")

if camera_input is not None:
    # Convert the image from Streamlit camera input to OpenCV format
    file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Get Aruco marker
    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:

        # Draw polygon around the marker
        int_corners = np.int0(corners)
        cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

        # Aruco Perimeter
        aruco_perimeter = cv2.arcLength(corners[0], True)

        # Pixel to cm ratio
        pixel_cm_ratio = aruco_perimeter / 20

        contours = detector.detect_objects(img)

        # Draw objects boundaries
        for cnt in contours:
            # Get rect
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            # Get Width and Height of the Objects by applying the Ratio pixel to cm
            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            # Display rectangle
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.polylines(img, [box], True, (255, 0, 0), 2)
            cv2.putText(img, "Width {} cm".format(round(object_width, 1)), (int(x - 100), int(y - 20)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            cv2.putText(img, "Height {} cm".format(round(object_height, 1)), (int(x - 100), int(y + 15)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

    # Display the processed image
    st.image(img, channels="BGR")

    # Add a download link for the processed image
    if st.button("이미지 다운로드"):
        # Save the processed image to a file
        cv2.imwrite('processed_image.jpg', img)
        with open('processed_image.jpg', "rb") as img_file:
            img_bytes = img_file.read()
        b64_img = base64.b64encode(img_bytes).decode()
        img_href = f'<a href="data:image/jpg;base64,{b64_img}" download="processed_image.jpg">다운로드</a>'
        st.markdown(img_href, unsafe_allow_html=True)
