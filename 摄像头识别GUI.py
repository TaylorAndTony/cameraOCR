from time import sleep

import yaml
from aip import AipOcr
from cv2 import cv2
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPlainTextEdit
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QTimer
from PySide2.QtCore import Signal,QObject
from pyperclip import copy
from threading import Thread

class UpSignal(QObject):
    text_out = Signal(QPlainTextEdit,str)

up_signal = UpSignal()

class UI:
    def __init__(self):
        # vars
        self.size = [640, 480]
        self.height = 100
        self.width = 400
        self.working = True
        self.ocr_now = False
        self.original = None
        self.left_top = ()
        self.right_bottom = ()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # ui
        self.app = QApplication([])
        self.window = QUiLoader().load('./res/ui.ui')
        # buttons
        self.window.addHeight.clicked.connect(self.addHeight)
        self.window.addWidth.clicked.connect(self.addWidth)
        self.window.decreaseHeight.clicked.connect(self.decreaseHeight)
        self.window.decreaseWidth.clicked.connect(self.decreaseWidth)
        self.window.resetSize.clicked.connect(self.resetSize)
        self.window.recognizeIt.clicked.connect(self.recognizeIt)
        self.window.exitNow.clicked.connect(self.exitNow)
        # threading
        up_signal.text_out.connect(self.setOutput)
        # timer
        self.timer = QTimer(self.window)  #初始化一个定时器
        self.timer.timeout.connect(self.timeout)  #计时结束调用operate()方法
        self.timer.start(50)  #设置计时间隔并启动

    def setOutput(self, obj, text):
        self.window.outText.setPlainText(text)

    def timeout(self):
        """ callback of timer """
        # read camera
        _, self.original = self.cap.read()
        # mark position
        self.left_top = (int((self.size[0] - self.width) / 2),
                         int((self.size[1] - self.height) / 2))
        self.right_bottom = (int((self.size[0] - self.width) / 2) + self.width,
                             int((self.size[1] - self.height) / 2) +
                             self.height)
        # 画框
        cv2.rectangle(self.original, self.left_top, self.right_bottom,
                      (0, 255, 0), 2)
        # 显示
        qimage = cvimg_to_qtimg(self.original)
        pixmap = QPixmap(qimage)
        self.window.imgLabel.setPixmap(pixmap)
        # whether to ocr it, if yes, threading to ocr.
        if self.ocr_now:
            self.ocr_now = False
            t = Thread(target=self.__ocrNow)
            t.setDaemon(True)
            t.start()

    def __ocrNow(self):
        # change to B&W, threading me
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        # crop it
        crop = gray[self.left_top[1]:self.right_bottom[1],
                    self.left_top[0]:self.right_bottom[0]]
        cv2.imwrite('crop.jpg', crop)
        print('cropped image saved')
        # 拿到结果
        result = neat_text(recognize('crop.jpg'))
        # 复制结果
        copy(result)
        print(result)
        # 输出结果
        up_signal.text_out.emit(self.window.outText, result)
        self.ocr_now = False
        print('operation finished')

    def addHeight(self):
        """ Callback button of addHeight """
        if self.height > self.size[1] - 40:
            self.height = self.size[1] - 40
        self.height += 30
        print('self.height', self.height)

    def addWidth(self):
        """ Callback button of addWidth """
        if self.width > self.size[0]:
            self.width = self.size[0]
        self.width += 30
        print('self.width', self.width)

    def decreaseHeight(self):
        """ Callback button of decreaseHeight """
        if self.height < 40:
            self.height = 40
        self.height -= 30
        print('self.height', self.height)

    def decreaseWidth(self):
        """ Callback button of decreaseWidth """
        if self.width < 30:
            self.width = 30
        self.width -= 30
        print('self.width', self.width)

    def resetSize(self):
        """ Callback button of resetSize """
        self.width = 400
        self.height = 120

    def recognizeIt(self):
        self.ocr_now = True

    def exitNow(self):
        self.cap.release()
        quit()

    def run(self):
        self.window.show()
        self.app.exec_()


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


def cvimg_to_qtimg(cvimg):
    """ opencv -> QImage """
    height, width, depth = cvimg.shape
    cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
    cvimg = QImage(cvimg.data, width, height, width * depth,
                   QImage.Format_RGB888)

    return cvimg


if __name__ == '__main__':
    ui = UI()
    ui.run()
