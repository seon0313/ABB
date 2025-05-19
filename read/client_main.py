import asyncio
import websockets
import json

async def websocket_client():
    uri = "ws://localhost:8765"
    
    try:
        # WebSocket 연결
        async with websockets.connect(uri) as websocket:
            print("connected")
            await websocket.send(json.dumps({
                'type': 'first',
                'data': 'robot'
            }))
            while True:
                pass
                
    except ConnectionRefusedError:
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(websocket_client())