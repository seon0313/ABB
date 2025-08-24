import cv2
import numpy as np

# ArUco 딕셔너리와 파라미터 설정
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
parameters = cv2.aruco.DetectorParameters()

# 카메라 캘리브레이션 데이터 (임시 값, 실제 캘리브레이션 필요)
# 예: 640x480 해상도의 카메라에 대한 임시 매트릭스
camera_matrix = np.array([[600, 0, 320],
                          [0, 600, 240],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1), dtype=np.float32)  # 왜곡 계수 (임시로 0)

# 마커의 실제 크기 (미터 단위, 예: 5cm)
marker_length = 0.05

# 이미지 로드
image_path = './markers/1.png'#"/home/SEON/Pictures/Screenshots/s.png"  # 감지할 이미지 경로
image = cv2.imread(image_path)
if image is None:
    print(f"이미지를 로드할 수 없습니다: {image_path}")
    exit()

# 마커 감지
corners, ids, rejected = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)

# 결과 처리
if ids is not None:
    print(f"감지된 마커 수: {len(ids)}")
    
    # 포즈 추정
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
    
    # 감지된 마커와 축 그리기
    for i in range(len(ids)):
        print(f"ID: {ids[i][0]}, 코너: {corners[i]}")
        
        # 마커 테두리 그리기
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
        # x, y, z 축 그리기
        cv2.drawFrameAxes(image, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], marker_length * 0.5)

else:
    print("마커를 감지하지 못했습니다.")

# 결과 표시 및 저장
cv2.imshow("Detected Markers with Axes", image)
cv2.imwrite("detected_5x5_marker_with_axes.png", image)
cv2.waitKey(0)
cv2.destroyAllWindows()