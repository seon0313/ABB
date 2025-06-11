import websockets
import asyncio
import time
import json
import cv2
import base64
import numpy as np

def __base64_to_image(base64_string):
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

if __name__=="__main__":


    async def connect():
        ws = await websockets.connect("ws://localhost:8765", ping_interval=None)
        msg = {
            'command': 'login',
            'password': '0000'
        }
        await ws.send(json.dumps(msg))
        a = await ws.recv()
        print('load!')
        old = None
        while True:
            msg = {
                'command': 'get_camera',
                #'value': 'marker'
            }
            await ws.send(json.dumps(msg))
            response = await ws.recv()
            data = json.loads(response)['data']
            print(data)
            cv2.imshow('cam', __base64_to_image(data))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(1/60)
            old = data
    asyncio.run(connect())