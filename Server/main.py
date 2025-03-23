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
import numpy as np
from io import BytesIO
import queue
import threading

client_queues = {}
clients_lock = threading.Lock()

save_data = {}
save_data_lock = threading.Lock()


# Base64 데이터를 이미지로 변환하는 함수
def base64_to_image(base64_string):
    # Base64 디코딩
    img_data = base64.b64decode(base64_string)
    # 바이트 데이터를 numpy 배열로 변환
    np_arr = np.frombuffer(img_data, np.uint8)
    # 이미지 디코딩
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

serverModuleList: dict = {}

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
        
        if type == 'bot':
            
            while True:
                a = {
                    'type': 'get_image',
                    'data': '',
                    'time': time.time() 
                }
                await websocket.recv(json.dumps(a))

        while True:
            data =  websocket.send(serverModuleList[type].run())
            await data[0]
            if data[1] != None:
                if data[1]['type'] == 'save':
                    with save_data_lock:
                        save_data[data[1]['data']['key']] = data[1]['data']['value']

            msg = await websocket.recv()
            print(f'get>>> {msg}')
            msg = json.loads(msg)
            if msg['type'] == 'image':
                img_data = base64_to_image(msg['data'])
                with save_data_lock:
                    save_data['image'] = img_data
                cv2.imshow('Real-time Image', img_data)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            elif msg['type'] == 'get':
                with save_data_lock:
                    result = {
                        'type': 'return',
                        'data': {
                            'key': msg['data'],
                            'value': save_data.get(msg['data'])
                        }
                    }
                    await websocket.send(json.dumps(result))

        return
        while True:
            # 클라이언트로부터 메시지 수신
            message = await websocket.recv()
            print(f"클라이언트로부터 받은 메시지: {message}")

            response = {'message': f"서버가 받은 메시지: {message}"}
            await websocket.send(json.dumps(response))
            print(f"클라이언트에게 보낸 메시지: {response}")
    except websockets.ConnectionClosed:
        print("클라이언트 연결이 종료되었습니다.")

# WebSocket 서버 시작 함수
async def start_server():
    # 서버를 localhost:8765에서 실행
    server = await websockets.serve(handle_connection, "0.0.0.0", 8765)
    print(f"Server Start [port: {8765}]")
    await server.wait_closed()

# 이벤트 루프 실행
if __name__ == "__main__":
    print('Module Loading')
    files = os.listdir('C:/Users/SEON/Documents/SBR/Server/serverEvent')
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