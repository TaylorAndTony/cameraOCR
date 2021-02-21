from pprint import pp, pprint
from time import sleep

import yaml
from aip import AipOcr
from cv2 import cv2
import keyboard


def recognize(image) -> dict:
    """ recognize words in the given image"""
    with open('settings.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    with open(image, 'rb') as f:
        img = f.read()

    APP_ID = config['APP_ID']
    API_KEY = config['API_KEY']
    SECRET_KEY = config['SECRET_KEY']
    FILE_NAME = config['FILE_NAME']

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    res = client.basicGeneral(img)
    # {'words_result': [{'words': '网友说:我之所以幸运,是因有他们保护】“无论'},
    #               {'words': '哪个时代都有这些最可爱的人,为了我们的安定生活'},
    #               {'words': '而守护。同样的年华,陪伴他们的不是手机、电脑和'},
    #               {'words': '游戏,而是雪山、钢枪和坚定的誓言。”#祖国山河'},
    #               {'words': '寸不能丢#,铭记英雄,致敬边防军人!'}],
    # 'log_id': 1363466493026631680,
    # 'words_result_num': 5}
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
        #     ocr_now = False
        #     cv2.imwrite('crop.jpg', crop)
        #     result = neat_text(recognize('crop.jpg'))
        #     print(result)
    cv2.destroyAllWindows()


def process_keyboard(e):
    global down, working, ocr
    if e.name == 's':
        ocr = True
    elif e.name == 'q':
        working = False
    elif e.name == 'a':
        down -= 10
    elif e.name == 'd':
        down += 10

if __name__ == '__main__':
    down = 260
    working = True
    ocr_now = False
    keyboard.hook(process_keyboard)
    cv_main_loop()
