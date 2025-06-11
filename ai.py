import cv2
import numpy as np
from event import EventListener
from multiprocessing import Event as mpEvent
from system import RobotSystem
from log import LogType
import heapq
import base64

class RoadNode:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0
    def __eq__(self, value):
        return self.position == value.position
    def __lt__(self, value):
        return self.f < value.f

class AI:
    def __init__(self, system: RobotSystem):
        self.__el: EventListener = EventListener('ai', self.__listener)
        self.__camera_el: EventListener = EventListener('camera', self.__cameraListener)
        self.__mpevent = mpEvent()
        self.__system = system

        self.__touchPos: tuple[int, int] = (0,0)

        self.__aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
        self.__parameters = cv2.aruco.DetectorParameters()

        # 카메라 캘리브레이션 데이터 (임시 값, 실제 캘리브레이션 필요)
        # 예: 640x480 해상도의 카메라에 대한 임시 매트릭스
        self.__camera_matrix = np.array([[600, 0, 320],
                                [0, 600, 240],
                                [0, 0, 1]], dtype=np.float32)
        self.__dist_coeffs = np.zeros((5, 1), dtype=np.float32)  # 왜곡 계수 (임시로 0)

        # 마커의 실제 크기 (미터 단위, 예: 5cm)
        self.__marker_length = 0.05
    def __cameraListener(self, data):
        print('@*!@*&*&@!*@!        CameraGet!!!!!!!!', flush=True)
        self.__system.values['camera'] = data
        self.__el.i(LogType.AI, 'cameraGet!')
    
    def __heuristc(self,node, goal, D=1, D2=2 ** 0.5):
        dx = abs(node.position[0] - goal.position[0])
        dy = abs(node.position[1] - goal.position[1])
        return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
    
    def __aStar(self,mapData, start, end):
        startNode = RoadNode(None, start)
        endNode = RoadNode(None, end)

        openList = []
        closedSet = set()

        heapq.heappush(openList, startNode)

        while openList:
            currentNode = heapq.heappop(openList)
            closedSet.add(currentNode.position)

            if currentNode == endNode:
                path = []
                while currentNode is not None:
                    path.append(currentNode.position)
                    currentNode = currentNode.parent
                return path[::-1]
            for newPosition in (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1):
                nodePosition = (currentNode.position[0] + newPosition[0], currentNode.position[1] + newPosition[1])

                if nodePosition[0] > len(mapData) - 1 or nodePosition[0] < 0 or nodePosition[1] > len(mapData[0]) - 1 or nodePosition[1] < 0:
                    continue

                if mapData[nodePosition[0]][nodePosition[1]] != 0:
                    continue

                new_node = RoadNode(currentNode, nodePosition)
                
                if new_node.position in closedSet:
                    continue

                new_node.g = currentNode.g + 1
                new_node.h = self.__heuristic(new_node, endNode)
                new_node.f = new_node.g + new_node.h

                if any(child for child in openList if new_node == child and new_node.g > child.g):
                    continue

                heapq.heappush(openList, new_node)
    
    def __listener(self, data: dict):
        if data.get('command') == 'touch':
            value = data.get('value')
            if value: self.__touchPos = (value[0], value[1])

    def run(self):
        self.__el.run()
        self.__camera_el.run()
        self.__el.i(LogType.AI, 'AI Start')
        return
        while not self.__mpevent.is_set():
            img = self.__system.values.get('camera')
            if img:
                if self.__touchPos != (0,0):

                    self.__touchPos = (0,0)

                markerImg = img
                
                corners, ids, rejected = cv2.aruco.detectMarkers(markerImg, self.__aruco_dict, parameters=self.__parameters)

                # 결과 처리
                if ids is not None:
                    print(f"감지된 마커 수: {len(ids)}")
                    # 포즈 추정
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, self.__marker_length, self.__camera_matrix, self.__dist_coeffs)
                    
                    # 감지된 마커와 축 그리기
                    for i in range(len(ids)):
                        print(f"ID: {ids[i][0]}, 코너: {corners[i]}")
                        # 마커 테두리 그리기
                        cv2.aruco.drawDetectedMarkers(markerImg, corners, ids)
                        # x, y, z 축 그리기
                        cv2.drawFrameAxes(markerImg, self.__camera_matrix, self.__dist_coeffs, rvecs[i], tvecs[i], self.__marker_length * 0.5)
                retval, buffer = cv2.imencode('.png', markerImg)
                if retval:
                    markerImg = base64.b64encode(buffer).decode('utf8')
                    print('!',markerImg, flush=True)
                    self.__system.values['marker_camera'] = markerImg
                    self.__el.sendEvent('server', {'type':'marker_camera', 'data':self.__system.values['marker_camera']})
                


    def close(self):
        self.__mpevent.set()