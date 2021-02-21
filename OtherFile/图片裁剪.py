from cv2 import cv2
from time import sleep
import BaiduAPI


cap = cv2.VideoCapture(0)
while True:
    ret, original = cap.read()
    # 640 * 480
    left_top = (80, 80)
    right_bottom = (560, 260)
    # 画框
    cv2.rectangle(original, left_top, right_bottom, (0, 255, 0), 2)
    # 显示图像
    cv2.imshow("frame", original)
    # 灰度图
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    # 裁剪
    crop = gray[left_top[1]:right_bottom[1], left_top[0]:right_bottom[0]]
    cv2.imshow("crop", crop)
    # 提交
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite('crop.jpg', crop)
        result = BaiduAPI.awesome_one_click_ocr('crop.jpg')
        print(result)
    # 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
