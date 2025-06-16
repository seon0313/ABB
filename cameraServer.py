from event import EventListener
from log import LogType
import socket
import threading
import base64
import numpy as np

class CameraServer:
    def __init__(self, host: '0.0.0.0', port=9119):
        self.__el: EventListener = EventListener('cameraServer')
        self.__server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__host = host
        self.__port = port
        self.__thread: threading.Thread = threading.Thread(target=self.__loop)
        self.__event: threading.Event = threading.Event()

        self.camera = ''

    def __base64_to_image(self, base64_string):
        img_data = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img

    def __send(self, data):
        self.__server.sendto(struct.pack('>Q', len(data)), (self.__host, self.__port))
        self.__server.sendto(data, (self.__host, self.__port))

    def __read(self) -> str:
        bs, addr = self.__server.recvfrom(8)
        (length,) = struct.unpack('>Q', bs)
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += self.__server.recvfrom(
                4096 if to_read > 4096 else to_read)[0]
        
        data = data.decode('utf8')
        #print('read:\t', data.split('value')[0], flush=True)
        return data
    
    def __loop(self):
        while not self.__event.is_set():
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
    
    def run(self):
        self.__el.run()
        self.__server.bind((self.__host, self.__port))