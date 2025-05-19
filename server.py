import asyncio
import websockets
import json
import base64
import numpy as np
import cv2
from system import Event, EventListener, RobotSystem
from log import LogType

class Server:
    def __init__(self, system: RobotSystem, host='0.0.0.0', port=8765):
        self.__host__ = host
        self.__port__ = port
        self.__server__: websockets.serve = None

        self.__system__ = system
        self.el = EventListener(self.listener)
        self.__system__.event.addListener('server', self.el)
        self.__system__.log.i(LogType.SERVER, "Server Load END")

    def listener(self, *arg):
        print('server Listener - port: ', self.__port__, 'args: ', arg)

    def base64_to_image(self, base64_string):
        # Base64 디코딩
        img_data = base64.b64decode(base64_string)
        # 바이트 데이터를 numpy 배열로 변환
        np_arr = np.frombuffer(img_data, np.uint8)
        # 이미지 디코딩
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    
    async def client(self, websocket):
        try:
            client_id = id(websocket)
            _ip, _port = websocket.remote_address
            self.__system__.log.i(LogType.SERVER,
                                  f"Connected New Client id: {client_id} | {_ip}:{_port}")

            pass

            self.__system__.log.i(LogType.SERVER,
                                  f"Disconnected Client id: {client_id} | {_ip}:{_port}")
        except Exception as e:
            self.__system__.log.e(LogType.SERVER,f"Client Error {e}")
    async def __start_server__(self):
        try:
            self.__system__.log.i(LogType.SERVER, "Opening Server...")
            self.__server__ = await websockets.serve(self.client, self.__host__, self.__port__)
            self.__system__.log.i(LogType.SERVER, "Server Opened")
            await self.__server__.wait_closed()
        except Exception as e:
            self.__system__.log.e(LogType.SERVER,
                                  f"Start Error - {e}")
    def close(self):
        if self.__server__:
            self.__server__.close()
        self.__system__.log.i(LogType.SERVER, "Server Close")
    def run(self):
        asyncio.run(self.__start_server__())