from AnyQt import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QImage
import sys
import utils.color_utils as c


class ColorTextField(QWidget):

  def __init__(self, key='', value=''):
      QWidget.__init__(self)


      self.textbox = QLineEdit()
      self.textbox.setText(value)

      self.label = QLabel(key)
      layout = QHBoxLayout(self)
      layout.addWidget(self.label)
      layout.addWidget(self.textbox)



class ColorEditingTool(QWidget):


    def __init__(self, img_blueprint, color_dict):
        super().__init__()

        self.title = 'Color Editing Tool'
        self.setWindowTitle(self.title)
        self.general_layout = QHBoxLayout(self);

        self.img_blueprint = img_blueprint[::2, ::2]
        self.color_dict = color_dict
        height, width = self.img_blueprint.shape
        self.img_width = width
        self.img_height = height
        self.move(100, 100)

        self.add_image()
        self.add_color_text_fields()

        ### end
        self.show()


    def add_color_text_fields(self):

        self.list_color_text_fields = []
        vertical_layout = QVBoxLayout();
        self.general_layout.addLayout(vertical_layout)
        self.general_layout.setAlignment(vertical_layout, QtCore.Qt.AlignRight)

        for key,value in self.color_dict.items():
            color_text_field = ColorTextField(str(key),value)
            self.list_color_text_fields += [color_text_field]

            vertical_layout.addWidget(color_text_field)
            vertical_layout.setAlignment(color_text_field, QtCore.Qt.AlignRight)
            color_text_field.textbox.textChanged.connect(self.color_text_changed)

        # vertical_layout.setSpacing(0)
        # vertical_layout.setContentsMargins(0,0,0,0)


    def generate_colored_image(self, color_dict):
        return c.replace_indices_with_colors(self.img_blueprint,color_dict).astype('uint8')


    def add_image(self):

        q_img = QImage(
            self.generate_colored_image(self.color_dict).tobytes(),
            self.img_height, self.img_width,
            QImage.Format_RGB888)

        self.img_label = QLabel()
        pixmap = QPixmap.fromImage(q_img)
        self.img_label.setPixmap(pixmap)
        self.general_layout.addWidget(self.img_label)

    def update_image(self,new_color_dict):
        new_img = self.generate_colored_image(new_color_dict)
        q_img = QImage(
            new_img.tobytes(),
            self.img_height, self.img_width,
            QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.img_label.setPixmap(pixmap)

    def color_text_changed(self):
        new_color_dict = { int(i.label.text()) : i.textbox.text() for i in self.list_color_text_fields }
        self.update_image(new_color_dict)
        print('Some values changed')
        print('\t',new_color_dict)