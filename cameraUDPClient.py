import socket
import base64
import cv2
import time

index = 0
arr = []
while True:
    cap = cv2.VideoCapture(index)
    if not cap.read()[0]:
        break
    else:
        arr.append(index)
    cap.release()
    index += 1
print('@@',arr)

# Create a VideoCapture object.  '0' is usually the default camera.
cap = cv2.VideoCapture(0)

time.sleep(2)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

host = '172.30.5.97'
port = 9119

server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server.connect((host, port))
while True:
    ret, frame = cap.read()
    print(frame)
    if not ret: break

    retval, buffer = cv2.imencode('.png', frame)
        
    if not retval:
        print("프레임 인코딩에 실패했습니다.")
        continue

    base64_bytes = base64.b64encode(buffer.tobytes())
    
    base64_string = base64_bytes.decode('utf-8')
    
    server.sendto(base64_string, (host, port))