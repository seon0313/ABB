import asyncio
import websockets
import json
import base64
import numpy as np
import cv2
from system import RobotSystem
from event import EventListener
from log import LogType
from multiprocessing import Event as mpEvent

class Server:
    def __init__(self, system: RobotSystem, host='0.0.0.0', port=8765):
        self.__host = host
        self.__port = port
        self.__server: websockets.serve = None

        self.__system = system
        self.eventListener = EventListener("server", self.__listener)

        self.__commands: dict = {
            'get': self.__commandGet,
            'info': self.__commandInfo,
            'get_commands': self.__commandGetcmds,
            'move': self.__commandMove,
            'camera': self.__commandCamera,
            'get_camera': self.__commandCameraGet,
            'touch': self.__commandTouch,
        }
        self.event = mpEvent()
        self.websocketList = []
    
    def __commandTouch(self, data):
        self.eventListener.sendEvent('ai', data)
    
    def __commandCamera(self, data: dict):
        #self.eventListener.i(LogType.SERVER, "Get Camera Data")
        self.__system.values['camera'] = data['data'].replace('data:image/png;base64,','')
        #self.eventListener.i(LogType.SERVER, str(type(self.__system.values['camera'])))
        self.eventListener.sendEvent('camera', self.__system.values['camera'])
    def __commandCameraGet(self, data: dict):
        self.eventListener.i(LogType.SERVER, data.get('marker_camera'))
        return {'commnad': data['command'], 'data':self.__system.values.get('camera' if not data.get('value') == 'marker' else 'marker_camera')}
    
    def __commandMove(self, data: dict):
        self.eventListener.sendEvent('controller', data)
    
    def __commandInfo(self, data: dict):
        return {'command':data['command'], 'name': self.__system.name, 'version': self.__system.version}
    
    def __commandGet(self, data: dict):
        self.eventListener.w(LogType.SERVER, f"{self.__system.values}")
        return self.__system.values
    def __commandGetcmds(self, data: dict):
        return {'command': data['command'], 'commands': [str(i) for i in self.__commands.keys()]}
    
    async def send(self, data):
        killList = []
        for i in self.websocketList:
            try:
                await i.send(data)
            except Exception as e:
                print('asdsd@as - ', e, flush=True)
                killList.append(i)
        for i in killList:
            del self.websocketList[self.websocketList.index(i)]

    def __listener(self, data: dict):
        if data.get('type') == 'log':
            try: asyncio.run(self.send(json.dumps({'command':'log', 'data': data['data']})))
            except:
                pass
        if data.get('type') == 'marker_camera':
            self.eventListener.i(LogType.SERVER, "get marker camera")
            self.__system.values['marker_camera'] = data.get('data')
    def __base64_to_image(self, base64_string):
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    
    async def __client(self, websocket):
        client_id = id(websocket)
        _ip, _port = websocket.remote_address
        self.eventListener.i(LogType.SERVER,
                                f"Connected New Client id: {client_id} | {_ip}:{_port}")
        logined = False
        while not self.event.is_set() and not logined:
            msg = await websocket.recv()
            msg: dict = json.loads(msg)
            if msg.get('command') == 'login':
                if msg.get('password') == self.__system.password:
                    logined = True
                    msg = {
                        'command': 'login', 'data': 'pass'
                    }
                    await websocket.send(json.dumps(msg))
                else:
                    msg = {
                        'command': 'login', 'data': 'need'
                    }
                    await websocket.send(json.dumps(msg))
            else:
                msg = {
                    'command': 'login', 'data': 'need'
                }
                await websocket.send(json.dumps(msg))
        self.websocketList.append(websocket)
        while not self.event.is_set():
            msg = await websocket.recv()
            msg = json.loads(msg)

            if self.__commands.get(msg['command']):
                value = self.__commands.get(msg['command'])(msg)
                if value: await websocket.send(json.dumps(value))
        #except Exception as e:
        #    self.__system__.log.e(LogType.SERVER, f'Error CLient id: {client_id} | {e}')
        self.eventListener.i(LogType.SERVER,
                                f"Disconnected Client id: {client_id} | {_ip}:{_port}")
        #except Exception as e:
        #    self.__system__.log.e(LogType.SERVER,f"Client Error {e}")
    async def __start_server(self):
        try:
            self.eventListener.i(LogType.SERVER, "Opening Server...")
            #loop = asyncio.new_event_loop()
            #asyncio.set_event_loop(loop)
            self.__server = await websockets.serve(self.__client, self.__host, self.__port)
            self.eventListener.i(LogType.SERVER, "Server Opened")
            await self.__server.wait_closed()
        except Exception as e:
            self.eventListener.e(LogType.SERVER,
                                  f"Start Error - {e}")
    def close(self):
        if self.__server:
            self.__server.close()
        self.eventListener.i(LogType.SERVER, "Server Close")
    def run(self, event):
        self.eventListener.run()
        self.event = event
        asyncio.run(self.__start_server())