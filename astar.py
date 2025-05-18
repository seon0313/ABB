# Time Complexity는 H에 따라 다르다.
# O(b^d), where d = depth, b = 각 노드의 하위 요소 수
# heapque를 이용하면 길을 출력할 때 reverse를 안해도 됨

import heapq  # priority queue
import pygame

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

def heuristic(node, goal, D=1, D2=2 ** 0.5):  # Diagonal Distance
    dx = abs(node.position[0] - goal.position[0])
    dy = abs(node.position[1] - goal.position[1])
    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

def aStar(maze, start, end):
    # startNode와 endNode 초기화
    startNode = Node(None, start)
    endNode = Node(None, end)

    # openList, closedList 초기화
    openList = []
    closedSet = set()

    # openList에 시작 노드 추가
    heapq.heappush(openList, startNode)

    # endNode를 찾을 때까지 실행
    while openList:
        # 현재 노드 지정
        currentNode = heapq.heappop(openList)
        closedSet.add(currentNode.position)

        # 현재 노드가 목적지면 current.position 추가하고
        # current의 부모로 이동
        if currentNode == endNode:
            path = []
            while currentNode is not None:
                path.append(currentNode.position)
                currentNode = currentNode.parent
            return path[::-1]

        # 인접한 xy좌표 전부, DFS
        for newPosition in (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1):
            # 노드 위치 업데이트
            nodePosition = (currentNode.position[0] + newPosition[0], currentNode.position[1] + newPosition[1])

             # 미로 maze index 범위 안에 있어야함
            if nodePosition[0] > len(maze) - 1 or nodePosition[0] < 0 or nodePosition[1] > len(maze[0]) - 1 or nodePosition[1] < 0:
                continue

            # 장애물이 있으면 다른 위치 불러오기
            if maze[nodePosition[0]][nodePosition[1]] != 0:
                continue

            new_node = Node(currentNode, nodePosition)
            # 자식이 closedList에 있으면 continue
            if new_node.position in closedSet:
                continue

            # f, g, h값 업데이트
            new_node.g = currentNode.g + 1
            new_node.h = heuristic(new_node, endNode)
            new_node.f = new_node.g + new_node.h

            # 자식이 openList에 있으고, g값이 더 크면 continue
            # new_node.g >= child.g 로 하면 openList 중복성을 줄일 수도 있습니다.
            # 하지만 이건 시나리오에 따라 다르고, 대부분 엄격히 더 낮은 g 값을 확인하면 충분할 수 있습니다.
            if any(child for child in openList if new_node == child and new_node.g > child.g):
                continue

            heapq.heappush(openList, new_node)

def main():
    maze = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    start = (0, 0)
    end = (7, 6)

    path = aStar(maze, start, end)
    print(path)
    if path:
        for y,i in enumerate(maze):
            for x,j in enumerate(i):
                if (x,y) == start: print('@', end=' ')
                elif (x,y) == end: print('&', end=' ')
                elif j: print('%', end=' ')
                elif (y,x) in path: print('-', end=' ')
                else: print('*', end=' ')
            print('')
        print("경로 발견:", path)
    else:
        print("경로를 찾을 수 없습니다.")


if __name__ == '__main__': main()