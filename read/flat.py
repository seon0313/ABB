import cv2
import numpy as np
import cv2.aruco as aruco

def flatten_image_with_single_aruco_marker(image_path, marker_output_size_px=200, target_id=None):
    """
    이미지에서 단일 ArUco 마커를 감지하고, 이를 기준으로 해당 마커를 평면화합니다.

    Args:
        image_path (str): 입력 이미지 파일 경로.
        marker_output_size_px (int): 평면화된 마커 이미지의 원하는 크기 (정사각형).
        target_id (int, optional): 감지할 특정 마커의 ID. None이면 감지된 첫 번째 마커를 사용합니다.

    Returns:
        numpy.ndarray: 평면화된 마커 이미지. 마커를 찾지 못하거나 오류 발생 시 None을 반환합니다.
    """
    # 1. 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"오류: {image_path} 에서 이미지를 로드할 수 없습니다.")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. ArUco 사전 및 파라미터 초기화
    # 사용할 ArUco 사전을 지정합니다. 이미지에 있는 마커와 일치해야 합니다.
    # 예: aruco.DICT_5X5_1000, aruco.DICT_4X4_250 등
    aruco_dict_type = aruco.DICT_5X5_1000 # 이미지의 마커에 따라 이 값을 변경하세요.

    try:
        # 최신 OpenCV 버전 (cv2.aruco.ArucoDetector 사용)
        dictionary = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    except AttributeError:
        # 이전 OpenCV 버전 (cv2.aruco.detectMarkers 사용)
        dictionary = aruco.Dictionary_get(aruco_dict_type)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dictionary, parameters=parameters)

    # 3. 마커가 감지되었는지 확인
    if ids is not None and len(ids) > 0:
        print(f"감지된 ArUco 마커 ID: {[id_val[0] for id_val in ids]}")

        selected_marker_corners = None
        selected_marker_id = -1

        if target_id is not None:
            for i, marker_id_val in enumerate(ids):
                if marker_id_val[0] == target_id:
                    selected_marker_corners = corners[i][0]
                    selected_marker_id = target_id
                    print(f"타겟 ID {target_id} 마커를 찾았습니다.")
                    break
            if selected_marker_corners is None:
                print(f"타겟 ID {target_id} 마커를 찾지 못했습니다. 감지된 첫 번째 마커를 사용합니다.")
        
        if selected_marker_corners is None: # 타겟 ID가 없거나, 타겟 ID를 못 찾은 경우
            selected_marker_corners = corners[0][0] # 첫 번째 감지된 마커 사용
            selected_marker_id = ids[0][0]
            print(f"ID {selected_marker_id} 마커를 사용하여 평면화를 진행합니다.")

        # 4. 소스 사각형의 꼭짓점 (선택된 단일 마커의 코너)
        # ArUco 코너 순서: 0:TL, 1:TR, 2:BR, 3:BL (마커 자체 기준, 시계방향)
        src_pts = np.array(selected_marker_corners, dtype="float32")

        # 5. 목적지 사각형의 꼭짓점 및 출력 이미지 크기 정의
        # 마커를 정사각형 형태로 평면화합니다.
        dst_pts = np.array([
            [0, 0],                                             # 결과 이미지의 Top-Left
            [marker_output_size_px - 1, 0],                     # 결과 이미지의 Top-Right
            [marker_output_size_px - 1, marker_output_size_px - 1], # 결과 이미지의 Bottom-Right
            [0, marker_output_size_px - 1]                      # 결과 이미지의 Bottom-Left
        ], dtype="float32")

        # 6. Perspective Transform Matrix 계산
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # 7. 이미지에 Perspective Transform 적용 (선택된 마커 평면화)
        # 원본 이미지 'img'에서 마커 영역을 잘라내어 변환하는 것이 아니라,
        # 변환 행렬 M을 전체 이미지에 적용하여 마커가 평면화된 뷰를 얻습니다.
        # 출력 크기는 정의된 marker_output_size_px X marker_output_size_px 입니다.
        warped_marker_image = cv2.warpPerspective(img, M, (marker_output_size_px, marker_output_size_px))
        
        return warped_marker_image
    else:
        print("ArUco 마커가 감지되지 않았습니다.")
        return None

# --- 사용 예시 ---
if __name__ == '__main__':
    # 사용자가 제공한 이미지 파일명을 사용합니다.
    # 이 스크립트와 같은 디렉토리에 이미지가 있다고 가정합니다.
    image_file = './read/map_top.png' # 실제 이미지 경로로 변경하세요.
                                     # 예: 'aruco_test_image.jpg'
    
    # 특정 ID의 마커를 사용하고 싶다면 target_id를 지정 (예: target_id=23)
    # None으로 두면 감지된 첫 번째 마커를 사용합니다.
    flattened_marker_img = flatten_image_with_single_aruco_marker(image_file, marker_output_size_px=300, target_id=11)

    if flattened_marker_img is not None:
        # 원본 이미지를 보여주고 싶다면 cv2.imread로 다시 로드
        original_img_display = cv2.imread(image_file)
        if original_img_display is not None:
            # 감지된 마커 코너를 원본 이미지에 그려서 확인 (선택 사항)
            # flatten_image_with_single_aruco_marker 함수에서 사용한 것과 동일한 사전 사용
            display_aruco_dict_type = aruco.DICT_5X5_1000 # 함수 내 사전과 일치시키세요.
            try:
                dictionary_disp = cv2.aruco.getPredefinedDictionary(display_aruco_dict_type)
                parameters_disp = cv2.aruco.DetectorParameters()
                detector_disp = cv2.aruco.ArucoDetector(dictionary_disp, parameters_disp)
                corners_disp, ids_disp, _ = detector_disp.detectMarkers(cv2.cvtColor(original_img_display, cv2.COLOR_BGR2GRAY))
            except AttributeError:
                dictionary_disp = aruco.Dictionary_get(display_aruco_dict_type)
                parameters_disp = aruco.DetectorParameters_create()
                corners_disp, ids_disp, _ = aruco.detectMarkers(cv2.cvtColor(original_img_display, cv2.COLOR_BGR2GRAY), dictionary_disp, parameters=parameters_disp)

            if ids_disp is not None and len(ids_disp) > 0:
                 cv2.aruco.drawDetectedMarkers(original_img_display, corners_disp, ids_disp)
            
            cv2.imshow("Original Image with Detected Markers", original_img_display)
        
        cv2.imshow("Flattened Single Marker", flattened_marker_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("단일 마커 평면화에 실패했습니다.")