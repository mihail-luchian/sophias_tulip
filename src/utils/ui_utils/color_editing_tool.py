from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage
import sys

class ColorEditingTool(QWidget):


    def __init__(self,img):
        super().__init__()

        self.title = 'Color Editing Tool'
        self.width = 1200
        self.height = 1200

        self.img = img[::4,::4,:]
        self.initUI()


    def initUI(self):

        self.setWindowTitle(self.title)

        height, width, channel = self.img.shape
        self.setGeometry(100,100, width*2, height)

        q_img = QImage(
            self.img.tobytes(),
            height, width,
            QImage.Format_RGB888)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap.fromImage(q_img)
        label.setPixmap(pixmap)