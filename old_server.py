import asyncio
import websockets
import json
from util import dcToJson
from system import message
import os
import cv2
import base64
import numpy as np
import time
from io import BytesIO
import queue
import threading

client_queues = {}
clients_lock = threading.Lock()

save_data = {}
save_data_lock = threading.Lock()
camera_matrix = np.array([[600, 0, 320],
                          [0, 600, 240],
                          [0, 0, 1]], dtype=np.float32)

# Base64 데이터를 이미지로 변환하는 함수
def base64_to_image(base64_string):
    # Base64 디코딩
    img_data = base64.b64decode(base64_string)
    # 바이트 데이터를 numpy 배열로 변환
    np_arr = np.frombuffer(img_data, np.uint8)
    # 이미지 디코딩
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img
marker_length = 0.05 # 5cm
serverModuleList: dict = {}
dist_coeffs = np.zeros((5, 1), dtype=np.float32)

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()

# 클라이언트가 연결될 때 호출되는 핸들러
async def handle_connection(websocket):
    try:
        client_id = id(websocket)
        _ip, _port = websocket.remote_address
        print(f"joined new client [{_ip}, {_port}]")
        message = await websocket.recv()
        message = json.loads(str(message))
        if message['type'] != 'first': return
        type = message['data']

        with clients_lock:
            client_queues[client_id] = queue.Queue()


        if type == 'robot':
            while True:
                print('???')
                a = {
                    'type': 'get_image',
                    'data': '',
                    'time': time.time() 
                }
                await websocket.send(json.dumps(a))
                msg = await websocket.recv()
                msg = json.loads(msg)
                if msg['type'] == 'image':
                    img_data = base64_to_image(msg['data'])
                    corners, ids, rejected = cv2.aruco.detectMarkers(img_data, aruco_dict, parameters=parameters)
                    if ids is not None:
                        print(f"감지된 마커 수: {len(ids)}")
                        
                        # 포즈 추정
                        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
                        
                        # 감지된 마커와 축 그리기
                        for i in range(len(ids)):
                            print(f"ID: {ids[i][0]}, 코너: {corners[i]}")
                            
                            # 마커 테두리 그리기
                            cv2.aruco.drawDetectedMarkers(img_data, corners, ids)
                            
                            # x, y, z 축 그리기
                            cv2.drawFrameAxes(img_data, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], marker_length * 0.5)
                    with save_data_lock:
                        save_data['image'] = img_data
                    cv2.imshow('Real-time Image', img_data)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    except websockets.ConnectionClosed:
        print("클라이언트 연결이 종료되었습니다.")

async def start_server():
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print(f"Server Start [port: {8765}]")
    await server.wait_closed()

if __name__ == "__main__":
    print('Module Loading')
    files = os.listdir('C:/Users/SEON/Documents/Project_ABB/Server/serverEvent')
    print(files)
    for i in files:
        print(i)
        if os.path.splitext(i)[1] == '.py':
            print('?',i)
            pkg = __import__(f'serverEvent.{i[:-3]}', fromlist=['EventModule'])
            print(pkg)
            name = pkg.EventModule().Name
            serverModuleList[name] = pkg.EventModule
    print(serverModuleList)
    asyncio.run(start_server())
    cv2.destroyAllWindows()