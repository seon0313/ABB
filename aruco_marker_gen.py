'''import cv2
import matplotlib.pyplot as plt

data = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)

print("[INFO] generating ArUCo tag type '{}' with ID '{}'".format('DICT_5X5_100', id))
img_size = 500

marker_img = cv2.aruco.generateImageMarker(data, id, img_size)
cv2.imwrite(str(id) + '.jpg', marker_img)

plt.imshow(marker_img)
plt.show()
'''
import cv2
import numpy as np
import matplotlib.pyplot as plt

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)

def generate_aruco_marker(marker_id, size=200):
    img = np.zeros((size, size, 1), dtype="uint8")
    img.fill(255)

    cv2.aruco.generateImageMarker(aruco_dict, marker_id, size, img, 1)
    
    cv2.imwrite(f"./markers/{marker_id}.png", img)
    #plt.imshow(img)
    #plt.show()

def getInt(msg: str = ':\t', re_try_msg: str = 're:\t') -> int:
    val = input(msg)
    while True:
        try:
            return int(val)
        except:
            val = input(re_try_msg)

if __name__ == '__main__':
    #marker_id = getInt('Enter marker_id:\t', 'enter only int:\t')
    marker_size = 200
    for i in range(400):
        generate_aruco_marker(i, marker_size)