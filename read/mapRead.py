import cv2
import numpy as np
import time

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
image_path = "image.png"  # 감지할 이미지 경로
image = cv2.imread(image_path)
if image is None:
    print(f"이미지를 로드할 수 없습니다: {image_path}")
    exit()
t= time.time()
# 마커 감지
corners, ids, rejected = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)
print(type(ids), ids)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 결과 처리
if ids is not None:
    print(f"감지된 마커 수: {len(ids)}")
    
    # 포즈 추정
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)

    edge = []
    map = [[]]
    
    # 감지된 마커와 축 그리기
    for i in range(len(ids)):
        #print(f"ID: {ids[i][0]}, 코너: {corners[i]}")
        
        # 마커 테두리 그리기
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
        # x, y, z 축 그리기
        cv2.drawFrameAxes(image, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], marker_length * 0.5)

        corner = corners[i][0]

        # 중심점 계산
        center_x = np.mean(corner[:, 0])  # x 좌표 평균
        center_y = np.mean(corner[:, 1])  # y 좌표 평균
        center = (int(center_x), int(center_y))
        edge.append([int(ids[i][0]), int(center_x), int(center_y)])
        cv2.circle(image, (int(center_x), int(center_y)), 5, (255,0,255), -1)
    
    center1 = tvecs[0].flatten()  # 첫 번째 마커 중심점 (x1, y1, z1)
    center2 = tvecs[1].flatten()  # 두 번째 마커 중심점 (x2, y2, z2)

    # 중심점 좌표 출력 (디버깅용)
    print(f"첫 번째 마커 중심점: {center1}")
    print(f"두 번째 마커 중심점: {center2}")

    # x, y 좌표 비교 (오차 허용 범위 확대)
    xy_tolerance = 1e-2  # 오차 허용 범위를 0.01로 확대
    if (abs(center1[0] - center2[0]) < xy_tolerance) and (abs(center1[1] - center2[1]) < xy_tolerance):
        print("두 마커는 x-y 평면에서 겹칩니다.")
    else:
        print("두 마커는 x-y 평면에서 겹치지 않습니다.")
        # 겹칠 수 있는 좌표 계산
        target_center2 = np.array([center1[0], center1[1], center2[2]])
        print(f"두 번째 마커를 겹치게 만들기 위한 좌표: {target_center2}")
        print(f"즉, 두 번째 마커를 ({center2[0]:.3f}, {center2[1]:.3f}, {center2[2]:.3f})에서 "
            f"({target_center2[0]:.3f}, {target_center2[1]:.3f}, {target_center2[2]:.3f})로 이동해야 합니다.")
        move_vector = target_center2 - center2
        print(f"이동 벡터: {move_vector}")

    # z 좌표 비교
    z_tolerance = 1e-3
    if abs(center1[2] - center2[2]) > z_tolerance:
        print("두 마커는 높이(z 좌표)가 다릅니다.")
    else:
        print("두 마커는 높이(z 좌표)가 동일합니다.")
        print("질문 조건(높이는 다름)을 만족하지 않습니다.")

    edge.sort(key=lambda x: x[0])
    x,y = (0,0)
    py = 0
    for index, i in enumerate(tuple(edge)):
        print('!!!', abs(x-i[1])+abs(y-i[2]))
        if index and abs(x-i[1])+abs(y-i[2]) > 200:
            py += 1
            map.append([])
        x,y = i[1], i[2]
        map[py].append(i[0])
    
    print(time.time()-t), '\t: 걸린시간'
    
    for i in map:
        for l in i:
            print('%10d' % l, end=' ')
        print()

else:
    print("마커를 감지하지 못했습니다.")

# 결과 표시 및 저장
cv2.imshow("Detected Markers with Axes", image)
cv2.imwrite("detected_5x5_marker_with_axes.png", image)
cv2.waitKey(0)
cv2.destroyAllWindows()