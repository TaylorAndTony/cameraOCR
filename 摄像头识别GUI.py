from threading import Thread
from time import sleep
from os import system
import webbrowser
from sys import exit

import yaml
import numpy as np
from aip import AipOcr
from cv2 import cv2
from pyperclip import copy
from PySide2.QtCore import QObject, QTimer, Signal
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPlainTextEdit, QLabel
from PIL.ImageQt import ImageQt
from PIL import Image


class UpSignal(QObject):
    text_out = Signal(QPlainTextEdit, str)
    set_image = Signal(QLabel, QPixmap)


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
        self.result = ''
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # ui
        self.app = 0
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
        self.window.searchOnline.clicked.connect(self.searchOnline)
        self.window.activeSoft.clicked.connect(self.camera_on)
        # threading
        up_signal.text_out.connect(self.setOutput)
        up_signal.set_image.connect(self.setPixmap)

    # -------------------------------------------
    #  camera part
    # -------------------------------------------

    def setOutput(self, obj, text):
        """ callback to set the output message """
        self.window.outText.setPlainText(text)

    def setPixmap(self, obj, pixmap):
        """ callback to set the image on the GUI """
        #   qimage = cvimg_to_qtimg(self.original)
        #   pixmap = QPixmap(qimage)
        self.window.imgLabel.setPixmap(pixmap)

    def camera_on(self):
        t = Thread(target=self.__timeout)
        t.setDaemon(1)
        t.start()
        print('界面更新线程已启动')

    def __timeout(self):
        """
        A loop to update the video using threading
        so call me using thread
        """
        while self.working:
            # read camera
            _, self.original = self.cap.read()
            # self.original: numpy.ndarray
            # mark position
            self.left_top = (int((self.size[0] - self.width) / 2),
                             int((self.size[1] - self.height) / 2))
            self.right_bottom = (int(
                (self.size[0] - self.width) / 2) + self.width,
                                 int((self.size[1] - self.height) / 2) +
                                 self.height)
            # 画框
            cv2.rectangle(self.original, self.left_top, self.right_bottom,
                          (0, 255, 0), 2)
            # - 显示
            # - cv2.original -> PIL Image -> QPixmap
            # 用cv2库将数据转为RGB通道图
            img = cv2.cvtColor(self.original, cv2.COLOR_BGR2RGB)
            # 利用PIL中的Image转化为QPixmap
            pil_img = Image.fromarray(img)
            # resize
            pil_img_resized = pil_img.resize((640, 480))
            pixmap = pil_img_resized.toqpixmap()
            up_signal.set_image.emit(self.window.imgLabel, pixmap)
            if self.ocr_now:
                self.ocr_now = False
                t = Thread(target=self.__ocrNow)
                t.setDaemon(True)
                t.start()
            sleep(0.07)

    # -------------------------------------------
    #  OCR Functions
    # -------------------------------------------

    def __ocrNow(self):
        """ sub func to OCR the text and insert value into the box """
        # change to B&W, threading me
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        # crop it
        crop = gray[self.left_top[1]:self.right_bottom[1],
                    self.left_top[0]:self.right_bottom[0]]
        cv2.imwrite('crop.jpg', crop)
        print('cropped image saved')
        # 拿到结果
        self.result = neat_text(recognize('crop.jpg'))
        # 复制结果
        copy(self.result)
        print(self.result)
        # 输出结果
        up_signal.text_out.emit(self.window.outText, self.result)
        self.ocr_now = False
        print('operation finished')

    def __search(self, text):
        """ search the text on baidu """
        url = f'https://www.baidu.com/s?ie=utf-8&wd={text}'
        print(url)
        webbrowser.open(url)

    def searchOnline(self):
        self.__ocrNow()
        sleep(0.1)
        if len(self.result) > 40:
            res = self.result[:40]
        else:
            res = self.result
        self.__search(res)

    # -------------------------------------------
    #  GUI operation
    # -------------------------------------------

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
        print('exit')
        self.working = False
        self.cap.release()
        quit()

    def closeEvent(self, event):
        print('exit')
        self.working = False
        self.cap.release()
        quit()


    def run(self):
        self.window.show()
        exit(self.app.exec_())


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
    # cvimg = QImage(cvimg.data, width, height, QImage.Format_RGB888)

    return cvimg


if __name__ == '__main__':
    ui = UI()
    ui.run()
