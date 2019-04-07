from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QVBoxLayout, QPushButton, \
    QColorDialog, QScrollArea
from PyQt5.QtGui import QIcon, QPixmap, QImage, QColor
import sys
import utils.color_utils as c


class ColorTextField(QWidget):

  def __init__(self, key='', value=''):
      QWidget.__init__(self)


      self.textbox = QLineEdit()
      self.textbox.setText(value)

      self.label = QLabel(key)
      self.button = QPushButton('x', self)
      self.button.setFixedWidth(20)

      layout = QHBoxLayout(self)
      layout.addWidget(self.label)
      layout.addWidget(self.textbox)
      layout.addWidget(self.button)



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
        self.showMaximized()


    def add_color_text_fields(self):

        self.color_field_dict = {}
        # adding a scroll area in case there are too many colors
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        self.general_layout.addWidget(scroll_area)

        # glue to attach the vertical layout to the scroll area
        glue_widget = QWidget()
        vertical_layout = QVBoxLayout();
        scroll_area.setWidget(glue_widget)
        glue_widget.setLayout(vertical_layout)

        for key,value in self.color_dict.items():
            color_text_field = ColorTextField(str(key),value)
            self.color_field_dict[key] = color_text_field

            vertical_layout.addWidget(color_text_field)
            vertical_layout.setAlignment(color_text_field, QtCore.Qt.AlignRight)
            color_text_field.textbox.textChanged.connect(self.color_text_changed)
            color_text_field.button.clicked.connect(lambda state,key=key: self.choose_color(key))


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
        self.img_label.mousePressEvent = self.get_pixel_pos
        self.general_layout.addWidget(self.img_label)

    def deselect_all_color_text_fields(self):
        for i,j in self.color_field_dict.items():
            j.textbox.deselect()

    def get_pixel_pos(self,event):

        self.deselect_all_color_text_fields()

        x = event.pos().x()
        y = event.pos().y()

        code = int(self.img_blueprint[y,x])
        self.color_field_dict[code].textbox.selectAll()
        self.color_field_dict[code].textbox.setFocus()
        print(x,y)

    def update_image(self,new_color_dict):
        new_img = self.generate_colored_image(new_color_dict)
        q_img = QImage(
            new_img.tobytes(),
            self.img_height, self.img_width,
            QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.img_label.setPixmap(pixmap)

    def color_text_changed(self):
        new_color_dict = {i : j.textbox.text() for i,j in self.color_field_dict.items()}
        self.update_image(new_color_dict)
        print('Some values changed')
        print('\t',new_color_dict)

    def choose_color(self,key):
        color_name = self.color_field_dict[key].textbox.text()
        current_color = QColor('#'+color_name)
        dialog = QColorDialog()


        color = dialog.getColor(current_color)
        if color.isValid():
            print(color.name())
            self.color_field_dict[key].textbox.setText(color.name()[-6:])