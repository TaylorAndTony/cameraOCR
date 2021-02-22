from pprint import pp, pprint
from time import sleep

import yaml
from aip import AipOcr
from cv2 import cv2
from pynput.keyboard import Key, Listener


def recognize(image) -> dict:
    """ recognize words in the given image"""
    with open('settings.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    with open(image, 'rb') as f:
        img = f.read()

    APP_ID = config['APP_ID']
    API_KEY = config['API_KEY']
    SECRET_KEY = config['SECRET_KEY']

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    res = client.basicGeneral(img)
    return res


def neat_text(dct) -> str:
    """ make the dictionary readable """
    words = dct['words_result']
    res = ''
    for line in words:
        res += line['words']
    return res


def cv_main_loop():
    """ the main loop of this program """
    global ocr_now
    cap = cv2.VideoCapture(0)
    while working:
        ret, original = cap.read()
        # 640 * 480
        left_top = (80, 80)
        right_bottom = (560, down)
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
        # if ocr_now:
        #     cv2.imwrite('crop.jpg', crop)
        #     result = neat_text(recognize('crop.jpg'))
        #     print(result)
        #     ocr_now = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if ocr_now:
            cv2.imwrite('crop.jpg', crop)
            result = neat_text(recognize('crop.jpg'))
            print(result)
            sleep(0.5)
            ocr_now = False
    cv2.destroyAllWindows()


def process_keyboard(key):
    global ocr_now
    global down
    global working
    try:
        btn = key.char
    except AttributeError:
        btn = None
    if btn == 's':
        ocr_now = True
    elif btn == 'a':
        down -= 10
    elif btn == 'd':
        down += 10
    elif btn == 'q':
        working = False
        quit()

if __name__ == '__main__':
    down = 260
    working = True
    ocr_now = False
    with Listener(on_press=process_keyboard) as listener:
        cv_main_loop()
        listener.join()
