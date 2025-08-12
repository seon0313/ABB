import socket

# 수신을 위한 소켓 설정
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind(('', 5891)) # 수신 포트 설정 (전송 포트와 동일해야 함)

# 메시지 수신 (수신 대기)
data, address = sock_recv.recvfrom(1024)

print(f"Received message from {address}: {data.decode()}")
sock_recv.close()