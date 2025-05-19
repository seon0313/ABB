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
        self.el = EventListener(self.__listener__)
        self.__system__.event.addListener('server', self.el)
        self.__system__.log.i(LogType.SERVER, "Server Load END")

    def __listener__(self, *arg):
        self.__system__.log.i(LogType.SERVER, f"change value: {self.__system__.values}")
        #print('server Listener - port: ', self.__port__, 'args: ', arg)

    def __base64_to_image__(self, base64_string):
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    
    async def __client__(self, websocket):
        #try:
        client_id = id(websocket)
        _ip, _port = websocket.remote_address
        self.__system__.log.i(LogType.SERVER,
                                f"Connected New Client id: {client_id} | {_ip}:{_port}")
        #try:
        while True:
            msg = await websocket.recv()
            msg = json.loads(msg)

            if msg['type'] == 'get':
                self.__system__.log.w(LogType.SERVER, f"{self.__system__.values}")
                await websocket.send(json.dumps(self.__system__.values))
        #except Exception as e:
        #    self.__system__.log.e(LogType.SERVER, f'Error CLient id: {client_id} | {e}')
        self.__system__.log.i(LogType.SERVER,
                                f"Disconnected Client id: {client_id} | {_ip}:{_port}")
        #except Exception as e:
        #    self.__system__.log.e(LogType.SERVER,f"Client Error {e}")
    async def __start_server__(self):
        try:
            self.__system__.log.i(LogType.SERVER, "Opening Server...")
            self.__server__ = await websockets.serve(self.__client__, self.__host__, self.__port__)
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