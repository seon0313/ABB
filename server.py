import asyncio
import websockets
import json
import base64
import numpy as np
import cv2

class Server:
    def __init__(self, host='0.0.0.0', port=8765):
        pass

    def base64_to_image(self, base64_string):
        # Base64 디코딩
        img_data = base64.b64decode(base64_string)
        # 바이트 데이터를 numpy 배열로 변환
        np_arr = np.frombuffer(img_data, np.uint8)
        # 이미지 디코딩
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    
    async def client(websocket):
        client_id = id(websocket)
        _ip, _port = websocket.remote_address
        print(f'joined new Client')

    def run():
        pass