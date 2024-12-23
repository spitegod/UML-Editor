import os
import sys
import json
import subprocess
import hashlib
from math import *
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from Static import Ui_StaticWidget  # Импортируем класс Ui_StaticWidget
from uml_elements import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QTime, QDateTime
from PyQt5.QtCore import pyqtSignal  # Импортируем pyqtSignal

from PyQt5.QtCore import Qt, QPointF, QLineF, QRectF, QEvent, QSize
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QKeySequence, QIcon, QCursor, QPainter, QPixmap


from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot

# class Hot_keys(QUndoCommand):
#     def __init__(self, scene, shape, shape_type, parent=None):
#         super().__init__(parent)
#         self.scene = scene
#         self.shape = shape
#         self.shape_type = shape_type

#     def undo(self): # Ctrl+Z
#         self.scene.removeItem(self.shape)  # Удаляем фигуру со сцены
#         self.scene.objectS_.remove(self.shape)  # Удаляем из списка объектов
#         # print(f"{self.shape_type} удален, объектов на сцене:", len(self.scene.objectS_))

#     def redo(self): # Ctrk+Y
#         self.scene.addItem(self.shape)  # Добавляем фигуру обратно на сцену
#         self.scene.objectS_.append(self.shape)  # Добавляем в список объектов
#         # print(f"{self.shape_type} добавлен, объектов на сцене:", len(self.scene.objectS_))

global_username = ""
global_start_time = None
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class EditingPanel(QWidget):
    def __init__(self, editable_item, main_window):
        super().__init__()
        self.editable_item = editable_item
        self.main_window = main_window

        # Используем QGridLayout
        self.layout = QGridLayout()
        self.label_choose = QLabel("Выберите элемент на сцене")
        self.layout.addWidget(self.label_choose, 0, 0)
        self.label_choose.setVisible(False)

        if isinstance(self.editable_item, Arrow):
            self.label_choose.setVisible(False)
            self.label_color = QLabel("Цвет стрекли")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_arrow_color)
            self.update_color_button_arrow()

            self.line_type_label = QLabel("Тип линии:")
            self.line_type_combo = QComboBox(self)
            self.line_type_combo.addItem(QIcon(QPixmap("imgs/solid_line.png")), "Сплошная")
            self.line_type_combo.addItem(QIcon(QPixmap("imgs/intermittemt_line.png")), "Пунктирная")
            self.line_type_combo.addItem(QIcon(QPixmap("imgs/point_line.png")), "Точечная")
            self.line_type_combo.addItem(QIcon(QPixmap("imgs/alternating_line.png")), "Чередующая")

            

            self.thickness_label = QLabel("Толщина линии:")
            self.thickness_spinbox = QSpinBox(self)
            self.thickness_spinbox.setRange(2, 5)
            self.thickness_spinbox.setValue(self.editable_item.pen_width)
            self.thickness_spinbox.valueChanged.connect(self.update_arrow_thickness)


            self.line_type_combo.currentTextChanged.connect(self.update_line_type)

            self.right_arrow_checkbox = QCheckBox("Наконечник справа")
            self.right_arrow_checkbox.setChecked(self.editable_item.right_arrow_enabled)
            self.right_arrow_checkbox.stateChanged.connect(self.toggle_right_arrow)

            self.left_arrow_checkbox = QCheckBox("Наконечник слева")
            self.left_arrow_checkbox.setChecked(self.editable_item.left_arrow_enabled)
            self.left_arrow_checkbox.stateChanged.connect(self.toggle_left_arrow)

            self.show_points_checkbox = QCheckBox("Показать точки")
            self.show_points_checkbox.setChecked(self.editable_item.show_points)
            self.show_points_checkbox.stateChanged.connect(self.toggle_points_visibility)

            self.layout.addWidget(self.label_color, 0, 0, 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.layout.addWidget(self.line_type_label, 1, 0)
            self.layout.addWidget(self.line_type_combo, 1, 1)
            self.layout.addWidget(self.thickness_label, 2, 0)
            self.layout.addWidget(self.thickness_spinbox, 2, 1)
            self.layout.addWidget(self.left_arrow_checkbox, 3, 0)
            self.layout.addWidget(self.right_arrow_checkbox, 3, 1)
            self.layout.addWidget(self.show_points_checkbox, 4, 0)

        elif isinstance(self.editable_item, Decision):
            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            
            self.layout.addWidget(self.label_color, 0, 0, 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.update_button_color()

        
        elif isinstance(self.editable_item, (StartEvent, EndEvent)):
            self.radius_label = QLabel("Радиус:")
            self.radius_spinbox = QSpinBox(self)
            self.radius_spinbox.setRange(5, 1000)
            self.radius_spinbox.setValue(int(self.editable_item.radius)) 
            self.radius_spinbox.valueChanged.connect(self.update_radius)
            
            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            self.layout.addWidget(self.label_color, 0, 0, 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.layout.addWidget(self.radius_label, 1, 0, 1, 1)
            self.layout.addWidget(self.radius_spinbox, 1, 1, 1, 1)

        elif isinstance(self.editable_item, (ActiveState)):
            self.width_label = QLabel("Ширина:")
            self.width_spinbox = QSpinBox(self)
            self.width_spinbox.setRange(10, 1000)
            self.width_spinbox.setValue(int(self.editable_item.boundingRect().width()))
            self.width_spinbox.valueChanged.connect(self.update_width)

            self.height_label = QLabel("Высота:")
            self.height_spinbox = QSpinBox(self)
            self.height_spinbox.setRange(10, 1000)
            self.height_spinbox.setValue(int(self.editable_item.boundingRect().height()))
            self.height_spinbox.valueChanged.connect(self.update_height)

            self.text_label = QLabel("Текст:")
            self.text_input = QLineEdit(self)
            self.text_input.setText(self.editable_item.text_item.toPlainText())
            self.text_input.setMaxLength(15)
            self.text_input.textChanged.connect(self.update_text)

            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            self.layout.addWidget(self.label_color, 0, 0 , 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.layout.addWidget(self.width_label, 1, 0, 1, 1)
            self.layout.addWidget(self.width_spinbox, 1, 1, 1, 1)
            self.layout.addWidget(self.height_label, 2, 0, 1, 1)
            self.layout.addWidget(self.height_spinbox, 2, 1, 1, 1)
            self.layout.addWidget(self.text_label, 3, 0, 1, 1)
            self.layout.addWidget(self.text_input, 3, 1, 1, 1)

        if isinstance(self.editable_item, (SignalSending, SignalReceipt)):
            self.width_label = QLabel("Ширина:")
            self.width_spinbox = QSpinBox(self)
            self.width_spinbox.setRange(10, 1000)
            self.width_spinbox.setValue(int(self.editable_item.boundingRect().width()))
            self.width_spinbox.valueChanged.connect(self.update_width)

            self.height_label = QLabel("Высота:")
            self.height_spinbox = QSpinBox(self)
            self.height_spinbox.setRange(10, 1000)
            self.height_spinbox.setValue(int(self.editable_item.boundingRect().height()))
            self.height_spinbox.valueChanged.connect(self.update_height)

            self.text_label = QLabel("Текст:")
            self.text_input = QLineEdit(self)
            self.text_input.setText(self.editable_item.text_item.toPlainText())
            self.text_input.setMaxLength(15)
            self.text_input.textChanged.connect(self.update_text)

            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            self.label_mirrow = QLabel("Отражение")
            self.mirrow_combo = QComboBox(self)
            self.mirrow_combo.addItem("Слева")
            self.mirrow_combo.addItem("Справа")
            # self.mirrow_combo.setItemText(str(self.editable_item.current_reflection))
            self.mirrow_combo.currentTextChanged.connect(self.change_mirror)

            if self.editable_item.current_reflection == "Слева":
                self.mirrow_combo.setCurrentIndex(0)
            else:
                self.mirrow_combo.setCurrentIndex(1)

            self.layout.addWidget(self.label_color, 0, 0 , 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.layout.addWidget(self.width_label, 1, 0, 1, 1)
            self.layout.addWidget(self.width_spinbox, 1, 1, 1, 1)
            self.layout.addWidget(self.height_label, 2, 0, 1, 1)
            self.layout.addWidget(self.height_spinbox, 2, 1, 1, 1)
            self.layout.addWidget(self.label_mirrow, 3, 0, 1, 1)
            self.layout.addWidget(self.mirrow_combo, 3, 1, 1, 1)
            self.layout.addWidget(self.text_label, 4, 0, 1, 1)
            self.layout.addWidget(self.text_input, 4, 1, 1, 1)

        elif isinstance(self.editable_item, (Splitter_Merge)):

            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            self.width_label = QLabel("Длинна:")
            self.width_spinbox = QSpinBox(self)
            self.width_spinbox.setRange(10, 1000)
            self.width_spinbox.setValue(int(self.editable_item.boundingRect().width()))
            self.width_spinbox.valueChanged.connect(self.update_width)

            self.height_label = QLabel("Толщина:")
            self.height_spinbox = QSpinBox(self)
            self.height_spinbox.setRange(10, 1000)
            self.height_spinbox.setValue(int(self.editable_item.boundingRect().height()))
            self.height_spinbox.valueChanged.connect(self.update_height)

            
            self.orint_label = QLabel("Положение:")
            self.orint_combo = QComboBox(self)
            self.orint_combo.addItem("Вериткально")
            self.orint_combo.addItem("Горизонатльно")
            self.orint_combo.currentTextChanged.connect(self.update_orientation)

            if self.editable_item.rotation() == 0: # Если горизонатльно, значит в combobox установится значение горизонатльно
                self.orint_combo.setCurrentIndex(1)
            else: # иначе вертикально
                self.orint_combo.setCurrentIndex(0)  

            self.layout.addWidget(self.label_color, 0, 0, 1, 1)
            self.layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.layout.addWidget(self.width_label, 1, 0, 1, 1)
            self.layout.addWidget(self.width_spinbox, 1, 1, 1, 1)
            self.layout.addWidget(self.height_label, 2, 0, 1, 1)
            self.layout.addWidget(self.height_spinbox, 2, 1, 1, 1)
            self.layout.addWidget(self.orint_label, 3, 0)
            self.layout.addWidget(self.orint_combo, 3, 1)
        
        elif isinstance(self.editable_item, (ImageItem)):

            self.opacity_label = QLabel("Прозрачность:")
            self.opacity_slider = QSlider(Qt.Horizontal)
            self.opacity_slider.setRange(0, 100)
            self.opacity_slider.setValue(int(self.editable_item.opacity() * 100))
            self.opacity_slider.valueChanged.connect(self.update_opacity)

            self.layout.addWidget(self.opacity_label, 0, 0, 1, 1)
            self.layout.addWidget(self.opacity_slider, 0, 1, 1, 1)

        elif isinstance(self.editable_item, (Text_Edit)): 
            self.text_label = QLabel("Текст:")

            # Создаем QTextEdit для отображения текста
            self.text_area = QTextEdit(self)

            # Устанавливаем начальный текст из editable_item.text_item в text_area
            self.text_area.setText(self.editable_item.toPlainText())

            # Подключаем сигнал textChanged от text_area, чтобы обновить текст в editable_item
            self.text_area.textChanged.connect(self.update_text)

            # Считываем и отображаем количество символов
            self.count_sim_label1 = QLabel("Количество символов - ")
            self.count_sim_input2 = QLineEdit("")
            self.count_sim_input2.setText(str(len(self.editable_item.toPlainText())))
            self.text_area.textChanged.connect(self.update_len_count)
            self.count_sim_input2.setReadOnly(True)
            self.count_sim_input2.setStyleSheet("""
                QLineEdit {
                    border: none;
                    background: transparent;
                                                }
""")
            self.max_length = 250  # Максимальная длина текста

             # Подключаем сигнал textChanged для отслеживания изменений
            self.text_area.textChanged.connect(self.max_length_text_area)
            # Добавляем виджеты в layout
            self.layout.addWidget(self.text_label, 0, 0, 1, 1)
            self.layout.addWidget(self.text_area, 1, 0, 1, 0)
            self.layout.addWidget(self.count_sim_label1, 2, 0, 1, 1)
            self.layout.addWidget(self.count_sim_input2, 2, 1, 1, 1)


        self.x_label = QLabel("X:")
        self.x_spinbox = QDoubleSpinBox(self)
        self.x_spinbox.setRange(-1000, 1000)  # Диапазон значений
        self.x_spinbox.setValue(editable_item.scenePos().x())
        # self.x_spinbox.valueChanged.connect(self.update_position)

        self.y_label = QLabel("Y:")
        self.y_spinbox = QDoubleSpinBox(self)
        self.y_spinbox.setRange(-1000, 1000)  # Диапазон значений
        self.y_spinbox.setValue(editable_item.scenePos().y())
        # self.y_spinbox.valueChanged.connect(self.update_position)

        self.x_spinbox.valueChanged.connect(self.update_position_from_spinbox)
        self.y_spinbox.valueChanged.connect(self.update_position_from_spinbox)
        self.is_position_updating = False

        self.main_window.scene_.coordinates_updated.connect(self.update_coordinates)

        self.mainwin = Ui_MainWindow()

        self.delete_item = QPushButton("Удалить")
        self.copy_item = QPushButton("Дублировать")


        # self.delete_item.clicked.connect(self.mainwin.delete_selected_item)

        self.delete_item.clicked.connect(self.delete_current_item)
        self.delete_item.setObjectName("DeleteButton")
        self.copy_item.clicked.connect(self.duplicate_current_item)


        self.layout.addWidget(self.x_label, 6, 0)
        self.layout.addWidget(self.x_spinbox, 6, 1)
        self.layout.addWidget(self.y_label, 7, 0)
        self.layout.addWidget(self.y_spinbox, 7, 1)
        self.layout.addWidget(self.delete_item, 8, 0)
        self.layout.addWidget(self.copy_item, 8, 1)

        if isinstance(self.editable_item, Arrow):
            self.x_label.setVisible(False)
            self.y_label.setVisible(False)
            self.x_spinbox.setVisible(False)
            self.y_spinbox.setVisible(False)
            self.copy_item.setVisible(False)
            self.layout.removeWidget(self.delete_item)
            self.layout.addWidget(self.delete_item, 4, 1)

        self.setLayout(self.layout)
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)
        self.setDesigh()

    def empty_panel(self):
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:  # Если это виджет, делаем его невидимым
                widget.setVisible(False)

        self.label_choose.setVisible(True)


    def delete_current_item(self):
        if self.editable_item:
            self.main_window.reset_inaction()
            # Если editable_item — это стрелка, удаляем стрелку
            if isinstance(self.editable_item, Arrow):
                self.editable_item.remove_arrow()  # Удаляем стрелку
                self.main_window.on_selection_changed()
                self.empty_panel()
            else:
                self.main_window.delete_specific_item(self.editable_item)  # Удаляем другой элемент  
                self.empty_panel()  

    def update_coordinates(self, x, y):
        if self.is_position_updating:
            return  # Прерываем, если уже идет обновление позиции
        self.is_position_updating = True  # Устанавливаем флаг
        self.x_spinbox.setValue(x)
        self.y_spinbox.setValue(-y)  # Инвертируем Y перед обновлением SpinBox
        self.is_position_updating = False

    #Если пользователь хочет поменять позицию объекта через панель редактирования
    def update_position_from_spinbox(self):
        self.main_window.reset_inaction()
        if self.is_position_updating:
            return  # Прерываем, если уже идет обновление позиции
        self.is_position_updating = True  # Устанавливаем флаг

        if self.editable_item:
            new_x = self.x_spinbox.value()
            new_y = -self.y_spinbox.value()  # Инвертируем значение Y только для SpinBox

            # Обновляем позицию объекта на сцене
            self.editable_item.setPos(new_x, new_y)

            # Передаем новые координаты центра объекта (если требуется)
            global_center = self.editable_item.mapToScene(self.editable_item.boundingRect().center())
            self.main_window.scene_.coordinates_updated.emit(global_center.x(), -global_center.y())  # Инвертируем Y только для передачи

        self.is_position_updating = False  # Сбрасываем флаг

    def change_arrow_color(self):
        self.main_window.reset_inaction()
        color = QColorDialog.getColor()
        if color.isValid():
            self.editable_item.change_color(color)
            self.update_color_button_arrow()

    def update_color_button_arrow(self):
        self.main_window.reset_inaction()
        current_color = self.editable_item.pen.color()  # Получаем цвет из pen у стрелки
        self.color_button.setStyleSheet(f"""
                background-color: {current_color.name()};
                border: 2px solid rgb(173, 173, 173);
""")

    def update_line_type(self):
        self.main_window.reset_inaction()
        line_type = self.line_type_combo.currentText()
        if line_type == "Пунктирная":
            self.editable_item.change_line_type("dashed")
        elif line_type == "Сплошная":
            self.editable_item.change_line_type("solid")
        elif line_type == "Точечная":
            self.editable_item.change_line_type("dotted")
        elif line_type == "Чередующая":
            self.editable_item.change_line_type("dash_dot")
        else:
            self.editable_item.change_line_type("solid")

    def toggle_right_arrow(self, state):
        self.main_window.reset_inaction()
        self.editable_item.right_arrow_enabled = bool(state)
        self.editable_item.update_arrow()

    def toggle_left_arrow(self, state):
        self.main_window.reset_inaction()
        self.editable_item.left_arrow_enabled = bool(state)
        self.editable_item.update_arrow()

    def toggle_points_visibility(self, state):
        self.main_window.reset_inaction()
        self.editable_item.show_points = bool(state)
        self.editable_item.update()

    def update_arrow_thickness(self, thickness):
        self.main_window.reset_inaction()
        self.editable_item.change_width(thickness)

    def update_text(self):
        self.main_window.reset_inaction()
        if hasattr(self.editable_item, 'text_item'):
            self.editable_item.text_item.setPlainText(self.text_input.text())
        if isinstance(self.editable_item, Text_Edit):
            new_text = self.text_area.toPlainText()
            self.editable_item.setPlainText(new_text)

    def update_len_count(self):
        self.count_sim_input2.setText(str(len(self.editable_item.toPlainText())))

    def max_length_text_area(self):
        current_text = self.text_area.toPlainText()

        # Если длина текста превышает максимальную длину, запрещаем ввод
        if len(current_text) > self.max_length:
           current_text = self.text_area.toPlainText()

        # Если длина текста превышает максимальную длину, запрещаем ввод
        if len(current_text) > self.max_length:
            # Отключаем добавление символов в текст
            cursor = self.text_area.textCursor()
            cursor.deletePreviousChar()  # Удаляем последний введенный символ
            self.text_area.setTextCursor(cursor)  # Применяем курсор

        # Обновляем количество символов в count_sim_input2
        self.update_len_count()

    def update_orientation(self):
        self.main_window.reset_inaction()
        if isinstance(self.editable_item, Splitter_Merge):
            orientation = self.orint_combo.currentText()  # Получаем выбранный текст
            if orientation == "Вериткально":
                width, height = self.editable_item.height, self.editable_item.width
                temp_s = width #Перед поворотом меняем ширину и высоту местами
                width = height
                height = temp_s
                rotation = 90
            elif orientation == "Горизонатльно":
                width, height = self.editable_item.width, self.editable_item.height
                rotation = 0
            else:
                return
            self.editable_item.update_size_and_orientation(width, height, rotation)


    def update_width(self):
        self.main_window.reset_inaction()
        new_width = self.width_spinbox.value()
        old_height = self.height_spinbox.value()

        if hasattr(self.editable_item, 'arrows') and self.editable_item.arrows:
            # Если у editable_item есть стрелки (арrows) и они не пустые
            for arrow in self.editable_item.arrows:
                arrow.update_arrow()  # Обновляем каждую стрелку
        if hasattr(self.editable_item, 'setRect'):
            current_x = self.x_spinbox.value() # Считывает текущее положение объекта по x из значения панели
            current_y = self.y_spinbox.value() # Считывает текущее положение объекта по y из значения панели
            self.editable_item.setRect(current_x, current_y, new_width, old_height)
            self.editable_item.update_text_position()
        elif hasattr(self.editable_item, 'update_size'):
            rect = self.editable_item.boundingRect()
            self.editable_item.update_size(new_width, old_height)
            self.editable_item.update_text_position()
        if isinstance(self.editable_item, QtWidgets.QGraphicsPolygonItem):
            self.update_polygon_size(new_width, old_height)
            if isinstance(self.editable_item, (SignalSending, SignalReceipt)):
                self.editable_item.reflect(self.mirrow_combo.currentText())
                self.editable_item.update_text_position()

    def update_height(self):
        self.main_window.reset_inaction()
        old_width = self.width_spinbox.value()
        new_height = self.height_spinbox.value()

        if hasattr(self.editable_item, 'arrows') and self.editable_item.arrows:
            # Если у editable_item есть стрелки (арrows) и они не пустые
            for arrow in self.editable_item.arrows:
                arrow.update_arrow()  # Обновляем каждую стрелку
        if hasattr(self.editable_item, 'setRect'):
            current_x = self.x_spinbox.value() # Считывает текущее положение объекта по x из значения панели
            current_y = self.y_spinbox.value() # Считывает текущее положение объекта по y из значения панели
            self.editable_item.setRect(current_x, current_y, old_width, new_height)
            self.editable_item.update_text_position()
        elif hasattr(self.editable_item, 'update_size'):
            rect = self.editable_item.boundingRect()
            self.editable_item.update_size(old_width, new_height)
            self.editable_item.update_text_position()
        elif isinstance(self.editable_item, QtWidgets.QGraphicsPolygonItem):
            self.update_polygon_size(old_width, new_height)
            if isinstance(self.editable_item, (SignalSending, SignalReceipt)):
                self.editable_item.reflect(self.mirrow_combo.currentText())
                self.editable_item.update_text_position()

    def update_polygon_size(self, new_width, new_height):
        polygon = self.editable_item.polygon()
        bounding_rect = polygon.boundingRect()

        # Коэффициенты масштабирования
        scale_x = new_width / bounding_rect.width() if bounding_rect.width() > 0 else 1
        scale_y = new_height / bounding_rect.height() if bounding_rect.height() > 0 else 1

        # Масштабируем каждую точку в многоугольнике
        new_polygon = QtGui.QPolygonF()
        for point in polygon:
            new_x = bounding_rect.x() + (point.x() - bounding_rect.x()) * scale_x
            new_y = bounding_rect.y() + (point.y() - bounding_rect.y()) * scale_y
            new_polygon.append(QtCore.QPointF(new_x, new_y))

        self.editable_item.setPolygon(new_polygon)

    def change_mirror(self, direction):
        self.main_window.reset_inaction()
        if isinstance(self.editable_item, QGraphicsPolygonItem):
            if direction == "Слева":
                self.editable_item.reflect("Слева")
                self.editable_item.trans = "Слева"
            elif direction == "Справа":
                self.editable_item.reflect("Справа")
                self.editable_item.trans = "Справа"

    def update_radius(self):
        self.main_window.reset_inaction()
        if isinstance(self.editable_item, (StartEvent)):
            new_radius = self.radius_spinbox.value()
            self.editable_item.setRadius(new_radius)  # Обновляем радиус
        if isinstance(self.editable_item, (EndEvent)):
            new_radius = self.radius_spinbox.value()
            self.editable_item.setRadius(new_radius)  # Обновляем радиус
            self.editable_item.update_inner_circle()

    def duplicate_current_item(self):
        if isinstance(self.editable_item, (StartEvent, Decision, EndEvent, ActiveState, SignalSending, SignalReceipt, Splitter_Merge, ImageItem, Text_Edit)):
            new_item = self.editable_item.clone()
            new_pos = self.editable_item.scenePos() + QPointF(10, 10)
            new_item.setPos(new_pos)

            self.main_window.scene_.addItem(new_item)

            self.main_window.objectS_.append(new_item)

            self.main_window.user_.add_action(f"Создан дубликат элемента '{self.editable_item.__class__.__name__}'", self.main_window.get_current_Realtime())
            self.main_window.user_actions.emit(
                self.main_window.user_.nickname,
                self.main_window.user_.user_id,
                self.main_window.user_.start_work,
                self.main_window.user_.end_work,
                next(reversed(self.main_window.user_.action_history)),
                next(reversed(self.main_window.user_.action_history.values())),
                self.main_window.user_.action_history
            )

            self.main_window.count_objectS.emit(len(self.main_window.objectS_))
            self.main_window.scene_.update()
            self.main_window.populate_object_list()


    def change_color(self):
        self.main_window.reset_inaction()
        color = QColorDialog.getColor()
        if color.isValid():
            self.editable_item.setBrush(QBrush(color))
            self.editable_item.color = color
            self.update_button_color()

    def update_button_color(self):
        self.main_window.reset_inaction()
        # Получение цвета из editable_item и установка его как цвет фона кнопки
        brush = self.editable_item.brush()
        if brush and brush.color().isValid():
            color = brush.color()
            self.color_button.setStyleSheet(f"""
                background-color: {color.name()};
                border: 2px solid rgb(173, 173, 173);
""")
        else:
            self.color_button.setStyleSheet("")

    #Прозрачность для ImageItem
    def update_opacity(self):
        self.main_window.reset_inaction()
        opacity = self.opacity_slider.value() / 100
        self.editable_item.setOpacity(opacity)

    def setDesigh(self):
        self.setStyleSheet("""
                           
        QWidget {
            font-family: 'Arial', sans-serif;
            font-size: 14px;
            color: #2f2f2f;
        }

        QLabel {
            font-size: 16px;
            font-weight: bold;
        }

        QSpinBox, QComboBox, QLineEdit, QTextEdit, QDoubleSpinBox {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            padding: 8px;
            font-family: 'Arial';
            font-size: 14px;
        }

        QSpinBox:hover, QComboBox:hover, QLineEdit:hover, QTextEdit:hover, QDoubleSpinBox::hover {
            border: 1px solid rgb(150, 150, 150);
        }

        QPushButton {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(150, 150, 150);
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            color: #2f2f2f;
        }

        QPushButton:hover {
            background-color: rgb(220, 220, 220);
            border: 1px solid rgb(100, 100, 100);
        }

        QPushButton:pressed {
            background-color: rgb(200, 200, 200);
        }
                           
        #DeleteButton:hover {
            background-color: rgba(255, 0, 0, 100);
            border: 1px solid rgb(150, 0, 0); 
        }

        #DeleteButton:pressed {
            background-color: rgb(200, 0, 0);
        }

        QCheckBox {
            font-size: 15px;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }

        QCheckBox::indicator:checked {
            background-color: rgb(150, 150, 150);
            border: 2px solid rgb(47, 47, 47);
        }

        QCheckBox::indicator:unchecked {
            background-color: rgb(240, 240, 240);
            border: 2px solid rgb(47, 47, 47);
        }

        QCheckBox::indicator:hover {
            background-color: rgba(190, 190, 190, 0.5);
        }
                           

        QSlider::groove:horizontal {
            height: 15px;
            background: rgb(220, 220, 220);
            border-radius: 5px;
        }

        QSlider::handle:horizontal {
            background: rgb(150, 150, 150);
            width: 14px;
            border-radius: 7px;
        }

        QSlider::handle:horizontal:pressed {
            background: white;
        }

        QGroupBox {
            border: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
            color: white;
        }

        QGroupBox::title {
            color: rgb(76, 175, 80);
            font-weight: bold;
        }


        QSpinBox, QDoubleSpinBox {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            padding: 4px;
            height: 28px;
        }

        /* Стиль кнопки для QSpinBox и QDoubleSpinBox */
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: rgb(240, 240, 240);
            border: none;
            width: 20px;
            height: 20px;
            border-radius: 6px;
        }

        /* Стиль стрелок вверх и вниз для QSpinBox и QDoubleSpinBox */
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            width: 16px;
            height: 16px;
            background: none;
            border: none;
        }

        /* Установка изображений для стрелок вверх и вниз */
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            image: url(imgs/tr_up.png);
            width: 12px;
            height: 12px;
        }

        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            image: url(imgs/tr_down.png);
            width: 12px;
            height: 12px;
        }
                            
        QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button, QComboBox::down-button {
            border: none;
            background: none;
            border-radius: 6px;
        }

        /*Наведение на кнопки*/
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover,
        QComboBox::down-button:hover {
            background-color: rgb(220, 220, 220);
        }
                           
        QComboBox::drop-down {
            width: 20px;
            border-left: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            background-color: rgb(240, 240, 240);
        }

        QComboBox::down-arrow {
            image: url(imgs/tr_down.png);
            width: 13px;
            height: 13px;
        }

        QComboBox QAbstractItemView {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            padding: 8px;
            font-family: 'Arial';
            font-size: 14px;
            selection-background-color: rgb(190, 190, 190);
            selection-color: white;
        }

        QComboBox QAbstractItemView::item {
            background-color: rgb(240, 240, 240);
            height: 30px;
            padding-left: 10px;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: rgb(76, 175, 80);
            color: white;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: rgba(0, 150, 136, 0.5);
        }


    """)


class DraggableButton(QtWidgets.QPushButton):
    def __init__(self, element_type, mainwindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.element_type = element_type  # Тип элемента, который будет создаваться

        self.setFixedSize(120, 65)

        self.mainwindow = mainwindow

        #Объекты, рисуемые в тулбаре
        self.decision_in_tulbar = self.create_desicion_in_tulbar()
        self.start_event_in_tulbar = self.create_start_event_in_tulbar()
        self.end_event_in_tulbar = self.create_end_event_in_tulbar()
        self.slitter_merge_h_in_tulbar = self.create_splitter_merge_horizontal_in_tulbar()
        self.slitter_merge_v_in_tulbar = self.create_splitter_merge_vertical_in_tulbar()
        self.sending_signal_in_tulbar = self.create_sending_signal_in_tulbar()
        self.sending_receipt_in_tulbar = self.create_sending_receipt_in_tulbar()
        self.active_state_in_tulbar = self.create_active_state_in_tulbar()
        self.text_edit_in_tulbar = self.create_text_edit_in_tulbar()

    #Рисуем объекты в тулбаре
    def create_desicion_in_tulbar(self):
        # В зависимости от element_type создаем соответствующий объект Decision
        if self.element_type == "Decision":
            return Decision(7, 0, 50, QtCore.Qt.white)

    def create_start_event_in_tulbar(self):
        # В зависимости от element_type создаем соответствующий объект Decision
        if self.element_type == "StartEvent":
            return StartEvent(0, 0, 30)

    def create_end_event_in_tulbar(self):
        if self.element_type == "EndEvent":
            return EndEvent(0, 0, 30, 0.5)

    def create_sending_signal_in_tulbar(self):
        if self.element_type == "SignalSending":
            return SignalSending(0, 25, 80, 50, "Справа")

    def create_sending_receipt_in_tulbar(self):
        if self.element_type == "SignalReceipt":
            return SignalReceipt(0, 25, 100, 50, "Слева")

    def create_splitter_merge_horizontal_in_tulbar(self):
        if self.element_type == "Splitter_Merge_Horizontal":
            return Splitter_Merge(0, 10, 100, 30, 0)

    def create_splitter_merge_vertical_in_tulbar(self):
        if self.element_type == "Splitter_Merge_Vertical":
            return Splitter_Merge(0, 0, 60, 30, 90)

    def create_active_state_in_tulbar(self):
        if self.element_type == "ActiveState":
            return ActiveState(-50, -30, 100, 60, 15)

    def create_text_edit_in_tulbar(self):
        if self.element_type == "Text_Edit":
            return Text_Edit(0, 0, 100, 30, text="Текст", max_length=250)



    def paintEvent(self, event):
        super().paintEvent(event)  # Вызовем родительский метод для отрисовки обычного вида кнопки

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Рисуем объект Decision
        if self.decision_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setBrush(self.decision_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            painter.drawPolygon(self.decision_in_tulbar.polygon())  # Рисуем полигон объекта Decision
            painter.restore()  # Восстанавливаем состояние рисования

        if self.start_event_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

            # Получаем границы эллипса и рисуем его
            rect = self.start_event_in_tulbar.boundingRect()
            painter.setBrush(self.start_event_in_tulbar.brush())  # Задаем цвет заливки
            painter.drawEllipse(rect)  # Рисуем эллипс
            painter.restore()

        if self.end_event_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

            # Рисование внешнего круга
            outer_rect = self.end_event_in_tulbar.boundingRect()
            painter.setBrush(self.end_event_in_tulbar.brush())  # Задаем цвет заливки для внешнего круга
            painter.drawEllipse(outer_rect)  # Рисуем внешний круг

            # Рисование внутреннего круга
            inner_radius = self.end_event_in_tulbar.radius * self.end_event_in_tulbar.inner_radius_ratio
            inner_rect = QtCore.QRectF(  # Здесь исправлено
                self.end_event_in_tulbar.x_center - inner_radius,
                self.end_event_in_tulbar.y_center - inner_radius,
                2 * inner_radius,
                2 * inner_radius
            )
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))  # Цвет внутреннего круга
            painter.drawEllipse(inner_rect)  # Рисуем внутренний круг

            painter.restore()  # Восстанавливаем состояние рисования

        if self.sending_signal_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setBrush(self.sending_signal_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            painter.drawPolygon(self.sending_signal_in_tulbar.polygon())  # Рисуем полигон объекта sending_signal
            painter.restore()  # Восстанавливаем состояние рисования

        if self.sending_receipt_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setBrush(self.sending_receipt_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            painter.drawPolygon(self.sending_receipt_in_tulbar.polygon())  # Рисуем полигон объекта sending_receipt
            painter.restore()  # Восстанавливаем состояние рисования

        if self.slitter_merge_h_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setBrush(self.slitter_merge_h_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            painter.drawPolygon(self.slitter_merge_h_in_tulbar.polygon())  # Рисуем полигон объекта slitter_merge_h
            painter.restore()  # Восстанавливаем состояние 
            
        if self.slitter_merge_v_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.rotate(90) #Поскольку объект изначально рисуется горизонтально, мы его поворачиваем
            painter.setBrush(self.slitter_merge_v_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
            painter.drawPolygon(self.slitter_merge_v_in_tulbar.polygon())  # Рисуем полигон объекта slitter_merge_v
            painter.restore()  # Восстанавливаем состояние рисования

        if self.active_state_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            # Получаем границы закругленного прямоугольника
            rect = self.active_state_in_tulbar.boundingRect()  # Убедитесь, что этот прямоугольник соответствует ожиданиям

            painter.setBrush(self.active_state_in_tulbar.brush())  # Задаем цвет заливки
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

            # Получаем радиус
            radius = self.active_state_in_tulbar.radius  # Убедитесь, что это значение корректное

            # Проверка, чтобы минимальный размер прямоугольника соответствовал радиусу
            effective_radius = min(radius, min(rect.width(), rect.height()) / 2)

            # Рисуем закругленный прямоугольник
            painter.drawRoundedRect(rect, effective_radius, effective_radius)  # Рисуем закругленный прямоугольник

            painter.restore()

        if self.text_edit_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.setPen(QtGui.QPen(QtCore.Qt.black))  # Устанавливаем цвет текста
            
            # Получаем текст из Text_Edit
            text = self.text_edit_in_tulbar.toPlainText()  # Здесь текст извлекается из Text_Edit

            # Рисуем текст, центрируем его
            text_rect = QtCore.QRectF(-self.width() // 2, -self.height() // 2, self.width(), self.height())
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, text)  # Рисуем текст
            painter.restore()

    def mouseMoveEvent(self, event):
        self.mainwindow.reset_inaction()
        # Проверяем, находится ли курсор внутри Text_Edit, если да, то игнорируем drag-and-drop
        if not self.underMouse():
            return

        if event.buttons() == Qt.LeftButton:
            mime_data = QtCore.QMimeData()
            #Перед отрисовкой объекта, определяем какой объект мы вообще собираемся вытащить из тулбара
            mime_data.setText(self.element_type)

            #Здесь создается перетаскиваемый объект из кнопки
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)

            pixmap = self.create_pixmap_for_drag() #Рисуем временный объект
            drag.setPixmap(pixmap)

            drag.setHotSpot(event.pos() - self.rect().topLeft())

            drag.exec_(Qt.MoveAction)

    def create_pixmap_for_drag(self):
        self.mainwindow.reset_inaction()
        pixmap = QtGui.QPixmap(self.size())  # Создаем отображениу временного объекта во время перетаскивания размером с кнопку
        pixmap.fill(QtCore.Qt.transparent)  # Делаем фон прозрачным

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.decision_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            # Создаем кисть с прозрачным цветом
            original_brush = self.decision_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.7)

            transparent_brush = QtGui.QBrush(color)
            painter.setBrush(transparent_brush)  # Устанавливаем прозрачную кисть
            
            # Устанавливаем прозрачную обводку
            pen_decision_color = color.darker(150)  
            pen_decision_color.setAlpha(200)  #сама обводка
            pen_decision = QtGui.QPen(pen_decision_color)  # Создаем перо с прозрачным цветом
            pen_decision.setWidth(2)  # Устанавливаем ширину обводки
            painter.setPen(pen_decision)  # Устанавливаем прозрачную обводку

            painter.drawPolygon(self.decision_in_tulbar.polygon())
            painter.restore()

        if self.start_event_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())

            # Получаем текущую кисть и её цвет
            brush = self.start_event_in_tulbar.brush()
            color = brush.color()
            color.setAlphaF(0.7) 
            
            # Создаём новую кисть с прозрачным цветом
            transparent_brush = QtGui.QBrush(color) 
            painter.setBrush(transparent_brush)

            # Устанавливаем прозрачную обводку
            pen_start_color = color.darker(150)
            pen_start_color.setAlpha(200)
            pen_start = QtGui.QPen(pen_start_color)  # Создаем перо с прозрачным цветом
            pen_start.setWidth(2)  # Устанавливаем ширину обводки
            painter.setPen(pen_start)  # Устанавливаем прозрачную обводку

            rect = self.start_event_in_tulbar.boundingRect()
            painter.drawEllipse(rect)
            painter.restore()

        if self.end_event_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            # Рисование внешнего круга с прозрачностью
            outer_radius = self.end_event_in_tulbar.radius  # Радиус внешнего круга
            outer_color = self.end_event_in_tulbar.brush().color()
            outer_color.setAlphaF(0.7)  # Устанавливаем прозрачность 30% для внешнего круга
            painter.setBrush(QtGui.QBrush(outer_color))  # Устанавливаем кисть с прозрачностью

            # Установка пера для обводки
            pen_outer = QtGui.QPen(outer_color.darker(150))
            pen_outer.setWidth(2)
            painter.setPen(pen_outer)
            painter.drawEllipse(-int(outer_radius), -int(outer_radius), int(2 * outer_radius), int(2 * outer_radius))  # Рисуем внешний круг

            # Рисование внутреннего круга с прозрачностью
            inner_radius = outer_radius * self.end_event_in_tulbar.inner_radius_ratio  # Внутренний радиус
            inner_color = QtGui.QColor(0, 0, 0, 100)
            painter.setBrush(QtGui.QBrush(inner_color))  # Устанавливаем кисть для внутреннего круга
            painter.setPen(QtCore.Qt.NoPen)  # Убираем обводку для внутреннего круга

            # Рисуем внутренний круг, который должен находиться в том же центре
            painter.drawEllipse(-int(inner_radius), -int(inner_radius), int(2 * inner_radius), int(2 * inner_radius))
            painter.restore()

        if self.sending_signal_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            # Задаем цвет заливки с прозрачностью
            original_brush = self.sending_signal_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.5)
            painter.setBrush(QtGui.QBrush(color))  # Устанавливаем прозрачную кисть

            # Рисуем полигон объекта sending_receipt
            painter.drawPolygon(self.sending_signal_in_tulbar.polygon())

            # Создаем прозрачную обводку
            pen_color = color.darker(150)
            pen_color.setAlpha(200)
            pen = QtGui.QPen(pen_color)  # Создаем перо с прозрачным цветом
            pen.setWidth(2)  # Устанавливаем ширину обводки
            painter.setPen(pen)

            # Рисуем тот же полигон с обводкой
            painter.drawPolygon(self.sending_signal_in_tulbar.polygon())

            painter.restore()  # Восстанавливаем состояние рисования

        if self.sending_receipt_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            # Задаем цвет заливки с прозрачностью
            original_brush = self.sending_receipt_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.5)
            painter.setBrush(QtGui.QBrush(color))  # Устанавливаем прозрачную кисть

            # Рисуем полигон объекта sending_receipt
            painter.drawPolygon(self.sending_receipt_in_tulbar.polygon())

            # Создаем прозрачную обводку
            pen_color = color.darker(150)
            pen_color.setAlpha(200)
            pen = QtGui.QPen(pen_color)  # Создаем перо с прозрачным цветом
            pen.setWidth(2)  # Устанавливаем ширину обводки
            painter.setPen(pen)

            # Рисуем тот же полигон с обводкой
            painter.drawPolygon(self.sending_receipt_in_tulbar.polygon())
            painter.restore()  # Восстанавливаем состояние рисования

        if self.slitter_merge_h_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            original_brush = self.slitter_merge_h_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.4)
            painter.setBrush(QtGui.QBrush(color))  # Устанавливаем прозрачную кисть

            # Рисуем полигон объекта slitter_merge_horizontal
            painter.drawPolygon(self.slitter_merge_h_in_tulbar.polygon())

            # Создаем прозрачную обводку
            pen_color = color.darker(150)
            pen_color.setAlpha(50)  
            pen = QtGui.QPen(pen_color)
            pen.setWidth(2) 
            painter.setPen(pen)  # Устанавливаем прозрачную обводку

            # Рисуем тот же полигон с обводкой
            painter.drawPolygon(self.slitter_merge_h_in_tulbar.polygon())

            painter.restore()
            
        if self.slitter_merge_v_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            painter.rotate(90)  # Поворачиваем на 90 градусов 
            original_brush = self.slitter_merge_v_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.4)
            painter.setBrush(QtGui.QBrush(color))  # Устанавливаем прозрачную кисть

            # Рисуем полигон объекта slitter_merge_vertical
            painter.drawPolygon(self.slitter_merge_v_in_tulbar.polygon())

            # Создаем прозрачную обводку
            pen_color = color.darker(150)
            pen_color.setAlpha(50)  
            pen = QtGui.QPen(pen_color)
            pen.setWidth(2) 
            painter.setPen(pen)  # Устанавливаем прозрачную обводку

            # Рисуем тот же полигон с обводкой
            painter.drawPolygon(self.slitter_merge_v_in_tulbar.polygon())

            painter.restore()


        if self.active_state_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки

            rect = self.active_state_in_tulbar.boundingRect()

            # Устанавливаем цвет заливки с прозрачностью
            original_brush = self.active_state_in_tulbar.brush()
            color = original_brush.color()
            color.setAlphaF(0.5) 
            painter.setBrush(QtGui.QBrush(color))  # Устанавливаем прозрачную кисть

            # Получаем радиус закргуленных углов
            radius = self.active_state_in_tulbar.radius

            # Проверка, чтобы минимальный размер прямоугольника соответствовал радиусу
            effective_radius = min(radius, min(rect.width(), rect.height()) / 2)

            # Рисуем закругленный прямоугольник
            painter.drawRoundedRect(rect, effective_radius, effective_radius)
            
            # Создаем прозрачную обводку
            pen_color = color.darker(150)
            pen_color.setAlpha(200) 
            pen = QtGui.QPen(pen_color)  # Создаем перо с прозрачным цветом
            pen.setWidth(2) 
            painter.setPen(pen)  # Устанавливаем прозрачную обводку

            # Рисуем закругленный прямоугольник с обводкой
            painter.drawRoundedRect(rect, effective_radius, effective_radius)

            painter.restore()

        if self.text_edit_in_tulbar:
            painter.save()
            painter.translate(self.rect().center())  # Перемещаем начало координат в центр кнопки
            
            # Устанавливаем цвет текста с прозрачностью
            text_color = QtGui.QColor(QtCore.Qt.black)
            text_color.setAlpha(127)  # Устанавливаем прозрачность 50%
            painter.setPen(QtGui.QPen(text_color))  # Устанавливаем цвет текста

            # Получаем текст из Text_Edit (по умолчанию как "Текст")
            text = self.text_edit_in_tulbar.toPlainText()

            # Рисуем текст
            text_rect = QtCore.QRectF(-self.width() // 2, -self.height() // 2, self.width(), self.height())
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, text)
            painter.restore()

        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        super().mousePressEvent(event)


class My_GraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label  # QLabel для обновления координат

    def leaveEvent(self, event):
        self.label.setText("(0, 0)")
        super().leaveEvent(event)


class My_GraphicsScene(QtWidgets.QGraphicsScene):
    coordinates_updated = pyqtSignal(float, float) #Сигнал, для отображения глобальныъ координат на панели редактирования
    def __init__(self, reset_time, objectS, user_, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_rect = None  # Прямоугольник для выделения
        self.start_pos = None  # Начальная позиция для выделения
        self.is_dragging = False  # Флаг, указывающий, что элемент перетаскивается
        # self.clicks = []  # Список для хранения информации о кликах
        self.reset_time = reset_time
        self.objectS = objectS
        self.user_ = user_
        self.label = label

        self.grid_step = 30  # Шаг сетки в пикселях
        self.grid_color = QtGui.QColor(200, 200, 200, 200) # Цвет линии сетки
        self.show_grid = False  # Флаг для отображения сетки (по умолчанию выключена)


    def drawBackground(self, painter, rect):
        # Включаем сглаживание
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Рисуем стандартный фон
        super().drawBackground(painter, rect)

        if self.show_grid:
            # Рисуем сетку
            left = int(rect.left()) - (int(rect.left()) % self.grid_step)
            top = int(rect.top()) - (int(rect.top()) % self.grid_step)

            painter.setPen(QtGui.QPen(self.grid_color, 0.5))  # Тонкая линия для сетки

            # Рисуем вертикальные линии
            x = left
            while x < rect.right():
                painter.drawLine(QtCore.QPointF(x, rect.top()), QtCore.QPointF(x, rect.bottom()))
                x += self.grid_step

            # Рисуем горизонтальные линии
            y = top
            while y < rect.bottom():
                painter.drawLine(QtCore.QPointF(rect.left(), y), QtCore.QPointF(rect.right(), y))
                y += self.grid_step

        # Переключение видимости сетки
    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.update()  # Перерисовываем сцену, чтобы отобразить изменения

    def mousePressEvent(self, event):

        # self.clicks.append(event.scenePos())
        self.reset_time.reset_inaction()
        selected_item = self.itemAt(event.scenePos(), QtGui.QTransform())  # Находим элемент под курсором
  
        if selected_item:
            self.is_dragging = True
            # Устанавливаем текст в label_x_y с названием класса элемента
            element_name = type(selected_item).__name__
            mouse_pos = event.scenePos()
            self.label.setText(f"({mouse_pos.x():.1f}, {-mouse_pos.y():.1f})\tВыбрано: {element_name}")
            # self.reset_time.on_object_selected(selected_item)

            item_rect = selected_item.sceneBoundingRect()
            item_center = item_rect.center()  # Центр объекта
            print(f"Выбран объект {element_name} с центром координат: ({item_center.x():.1f}, {-item_center.y():.1f})")

            # Показ панели редактирования
            if isinstance(selected_item, (InnerCircle, Text_into_object)): #Проверяем нажал ли пользователь на дочерний элемент
                parent_item = selected_item.parentItem()  # Получаем родителя
                if isinstance(parent_item, (EndEvent, ActiveState, SignalReceipt, SignalSending)):
                    self.reset_time.show_editing_panel(parent_item) # Окно редактирования будет отоброжать информацию для родительского элемента
                    item_i = self.objectS.index(parent_item)
                    self.reset_time.object_panel_select(item_i)
            elif not(isinstance(selected_item, Arrow)): # Если нет, по умолчанию отобразим информацию о selected_item
                self.reset_time.show_editing_panel(selected_item)
                item_i = self.objectS.index(selected_item)
                self.reset_time.object_panel_select(item_i)
            else:
                self.reset_time.show_editing_panel(selected_item)
            

        else:
            self.reset_time.on_selection_changed()
            self.is_dragging = False
            mouse_pos = event.scenePos()
            self.label.setText(f"({mouse_pos.x():.1f}, {-mouse_pos.y():.1f})")

        if not self.is_dragging:  # Начинаем рисовать прямоугольник выделения is_dragging = True
            if event.button() == QtCore.Qt.LeftButton:
                self.start_pos = event.scenePos()  # Запоминаем начальную точку выделения
                if self.selection_rect is None:
                    self.selection_rect = QtWidgets.QGraphicsRectItem()
                    self.selection_rect.setPen(QtGui.QPen(QtGui.QColor(125, 125, 125, 150)))  # линия для выделения
                    self.selection_rect.setBrush(QtGui.QBrush(QtGui.QColor(150, 150, 150, 50)))  # Прозрачный цвет внутри
                    self.addItem(self.selection_rect)  # Добавляем прямоугольник на сцену, который служит для выделения объектов на сцене

        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        mouse_pos = event.scenePos()
        self.label.setText(f"({mouse_pos.x():.1f}, {-mouse_pos.y():.1f})")
        self.reset_time.stop_inaction()
        if not self.is_dragging:  # Обновляем прямоугольник выделения только если не перетаскиваем
            if self.selection_rect and self.start_pos:
                rect = QtCore.QRectF(self.start_pos, event.scenePos()).normalized()
                self.selection_rect.setRect(rect)  # Обновляем прямоугольник
        super().mouseMoveEvent(event)
        

    def mouseReleaseEvent(self, event):
        if self.selection_rect:
            selected_items = self.items(self.selection_rect.rect())  # Находим все элементы внутри прямоугольника
            for item in selected_items:
                item.setSelected(True)  # Выделяем элементы

            self.removeItem(self.selection_rect)  # Убираем прямоугольник с экрана
            self.selection_rect = None  # Очищаем ссылку на прямоугольник

        self.is_dragging = False  # Снимаем флаг перетаскивания
        super().mouseReleaseEvent(event)
    
    def dragEnterEvent(self, event):
        self.reset_time.reset_inaction()
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.reset_time.reset_inaction()
        element_type = event.mimeData().text()
        position = event.scenePos()

        item = None  

        if element_type == "Decision":
            item = Decision(position.x(), position.y(), 50)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "StartEvent":
            item = StartEvent(position.x(), position.y(), 30)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "EndEvent":
            item = EndEvent(position.x(), position.y(), 30, 0.5)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "ActiveState":
            item = ActiveState(position.x(), position.y(), 100, 60, 15)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "SignalSending":
            item = SignalSending(position.x(), position.y(), 160, 60, "Справа")
            item.reflect("Справа")
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "SignalReceipt":
            item = SignalReceipt(position.x(), position.y(), 180, 60, "Слева")
            item.reflect("Слева")
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "Splitter_Merge_Horizontal":
            item = Splitter_Merge(position.x(), position.y(), 120, 40, 0)
            item.setRotation(0)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "Splitter_Merge_Vertical":
            item = Splitter_Merge(position.x(), position.y(), 120, 40, 90)
            item.setRotation(90)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "Text_Edit":
            item = Text_Edit(position.x(), position.y(), 100, 30, text="Текст", max_length=250)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        if item:
            self.addItem(item)
            self.objectS.append(item)

            self.reset_time.show_editing_panel(item)

            self.user_.add_action(
                f"Добавлен элемент '{item.__class__.__name__}'", 
                self.reset_time.get_current_Realtime()
            )
            self.reset_time.user_actions.emit(
                self.user_.nickname, 
                self.user_.user_id, 
                self.user_.start_work, 
                self.user_.end_work,
                next(reversed(self.user_.action_history)),
                next(reversed(self.user_.action_history.values())), 
                self.user_.action_history
            )
            self.reset_time.populate_object_list()
            event.acceptProposedAction()

            global_pos = item.mapToScene(item.pos())
            self.coordinates_updated.emit(global_pos.x(), global_pos.y()) #Передача глобальных координатов в панель редактирования

            # Проверяем переполнение
            if len(self.objectS) > 50:
                self.reset_time.message_overcrowed_objectS()
        else:
            # Если item (например фрагмент Text_Edit)не распознан, отклоняем событие
            event.ignore()

    def dragMoveEvent(self, event):
        self.reset_time.reset_inaction()
        event.acceptProposedAction()

    # def addShape(self, shape):
    #     # Создаем команду для добавления фигуры
    #     add_command = Hot_keys(self, shape)
    #     self.undo_stack.push(add_command)  # Добавляем команду в стек отмены

    # def keyPressEvent(self, event):
    #     # Реализуем действие для Ctrl+Z
    #     if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
    #         self.undo_stack.undo()  # Отменяем последнее действие
    #     elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
    #         self.undo_stack.redo()  # Повторяем отмененное действие
    #     else:
    #         super().keyPressEvent(event)

    # def has_clicks(self):
    #     return len(self.clicks) > 0



#Класс с информацией об одном Пользователе
class User:
    def __init__(self, nickname: str, user_id: int, start_work: str, end_work: str) -> None:
        self.nickname = nickname
        self.user_id = user_id
        self.action_history = {}  # Хэш-таблица для хранения истории действий с временными метками
        self.start_work = start_work #"dd.MM.yyyy HH:mm:ss"
        self.end_work = end_work #"dd.MM.yyyy HH:mm:ss"
        # self.count_elements = count_elements #Длинна списка objectS_


    def add_action(self, action: str, time: str) -> None:
        self.action_history[time] = action  # Время как ключ, действие как значение

    def pop_action(self, time: str = None) -> None:
        if time:
            # Удаляем действие по времени
            removed_action = self.action_history.pop(time, None)
            
        else:
            # Удаляем последнее добавленное действие
            if self.action_history:
                time, removed_action = self.action_history.popitem()


#Класс в котором хранится массив с информацией о пользователях
class UserManager:
    def __init__(self):
        self.users = []  # Список пользователей

    def add_user(self, user: User) -> None:
        """Добавляет пользователя в список."""
        self.users.append(user)
    
    def get_user(self, _id: int) -> User:
        for user in self.users:
            if user.user_id == _id:
                return user
        raise ValueError(f"Пользователя с id: {_id} нет!")



os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Окно Помощь
class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Помощь")
        self.setGeometry(100, 100, 600, 600)
        self.setWindowIcon(QIcon("imgs/main_icon.png"))

        layout = QVBoxLayout()
        
        # Поле для поиска
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск по тексту...")
        self.search_input.textChanged.connect(self.search_text)
        
        # Кнопка для поиска
        self.search_button = QPushButton("Поиск", self)
        self.search_button.clicked.connect(self.search_text)
        
        # Ход layout для поиска
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # Текстовое поле с инструкциями
        self.instruction_text = QTextEdit()
        self.instruction_text.setReadOnly(True)
        self.instruction_text.setText(self.load_instruction())
        
        layout.addLayout(search_layout)  # Добавляем layout поиска
        layout.addWidget(self.instruction_text)  # Добавляем QTextEdit
        
        self.setLayout(layout)

        self.setDesign()

    def load_instruction(self):
        # Загружаем текст инструкции из файла
        instruction_path = os.path.join(os.path.dirname(__file__), 'readme.txt')
        try:
            with open(instruction_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:  # Попробуем открыть в кодировке windows-1251
            try:
                with open(instruction_path, 'r', encoding='windows-1251') as file:
                    return file.read()
            except FileNotFoundError:
                return "Файл с инструкцией не найден."
            except Exception as e:
                return f"Ошибка при загрузке инструкции: {e}"
        except FileNotFoundError:
            return "Файл с инструкцией не найден."
        except Exception as e:
            return f"Ошибка при загрузке инструкции: {e}"

    def search_text(self):
        # Получаем текст для поиска
        search_term = self.search_input.text()

        # Очищаем любые предыдущие выделения
        cursor = self.instruction_text.textCursor()
        cursor.setPosition(0)  # Сбросить курсор в начало
        self.instruction_text.setTextCursor(cursor)

        if search_term:
            # Ищем текст и выделяем все совпадения
            document = self.instruction_text.document()
            cursor = document.find(search_term)

            while not cursor.isNull():
                self.highlight_cursor(cursor)
                cursor = document.find(search_term, cursor)

        else:
            # Если поле поиска пустое, сбрасываем выделения
            self.instruction_text.setTextCursor(cursor)

    def highlight_cursor(self, cursor):
        # Метод для выделения найденного текста
        cursor.select(cursor.WordUnderCursor)  # Выделить найденное слово
        self.instruction_text.setTextCursor(cursor)

    def setDesign(self):
        self.setStyleSheet("""
         /* Общий стиль окна */
        QWidget {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
            color: #333;
        }

        /* Заголовок окна */
        QDialog {
            background-color: #2c3e50;
            color: #fff;
        }

        QTextEdit {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            color: #333;
            selection-background-color: #3498db;
            selection-color: white;
        }

        QTextEdit::cursor {
            color: #3498db;
        }

        QLineEdit {
            padding: 6px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 6px;
            margin: 10px;
        }

        QPushButton {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(150, 150, 150);
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: rgb(220, 220, 220); 
            border: 1px solid rgb(100, 100, 100); 
        }

        QPushButton:pressed {
            background-color: rgb(200, 200, 200); 
        }

        /* Стиль для вертикальных и горизонтальных скроллеров */
        QScrollBar:vertical {
            border: none;
            background: none;
            width: 12px;
            margin: 5px 0 5px 0;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: rgb(200, 200, 200);
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgb(180, 180, 180);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background: none;
            height: 12px;
            margin: 0px 5px 0px 5px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: rgb(200, 200, 200);
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal:hover {
            background: rgb(180, 180, 180);
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
            width: 0px;
        }
        /* Установим кнопки и отступы */
        QVBoxLayout {
            spacing: 10px;
            margin: 10px;
        }
""")

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(139, 136)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.pushButton_BGcolor = QtWidgets.QPushButton(Dialog)
        self.pushButton_BGcolor.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.pushButton_BGcolor.setText("")
        self.pushButton_BGcolor.setObjectName("pushButton_BGcolor")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton_BGcolor)
        self.lineEdit_text = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_text.setText("")
        self.lineEdit_text.setObjectName("lineEdit_text")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_text)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_delete = QtWidgets.QPushButton(Dialog)
        self.pushButton_delete.setStyleSheet("color: rgb(255, 0, 0);")
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.horizontalLayout_2.addWidget(self.pushButton_delete)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.pushButton_copy = QtWidgets.QPushButton(Dialog)
        self.pushButton_copy.setObjectName("pushButton_copy")
        self.horizontalLayout_2.addWidget(self.pushButton_copy)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(Dialog)
        self.line_2.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        

        self.retranslateUi(Dialog)
        
        # Подключение сигнала нажатия кнопки к слоту
        self.pushButton_BGcolor.clicked.connect(self.open_color_dialog)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Управление"))
        self.label_4.setText(_translate("Dialog", "Управление"))
        self.label.setText(_translate("Dialog", "Цвет"))
        self.label_2.setText(_translate("Dialog", "Tекст"))
        self.pushButton_delete.setText(_translate("Dialog", "Удалить"))
        self.pushButton_copy.setText(_translate("Dialog", "Копировать"))

    def open_color_dialog(self):
        # Открытие диалогового окна выбора цвета
        color = QtWidgets.QColorDialog.getColor()

        # Если цвет выбран, изменить цвет кнопки
        if color.isValid():
            self.pushButton_BGcolor.setStyleSheet(f"background-color: {color.name()};")
            self.lineEdit_text.setStyleSheet(f"QLineEdit {{ color: {color.name()} }}")#цвет текста
#----------------------------------

# Класс для создания диалогового окна, наследуемый от QDialog
class DialogWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()  # Экземпляр класса интерфейса
        self.ui.setupUi(self)  # Настройка интерфейса в окне

#Класс для создания кастомного заголовка для LoginWindow
class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        self.setFixedHeight(35)

        # Layout для кастомного заголовка
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("", self)
        self.title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        # Кнопка закрытия
        self.close_button = QPushButton(self)
        self.close_button.setIcon(QIcon("imgs/close_login.png"))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setIconSize(QSize(14, 14))
        self.close_button.clicked.connect(self.close_window)
        layout.addWidget(self.close_button, alignment=QtCore.Qt.AlignRight) # Перемещаем кнопку вправо

        self.setLayout(layout)

    # Закрытие окна регистрации и выход из приложения
    def close_window(self):
        self.window().close()

    # Нажатие на title
    def mousePressEvent(self, event):
        self.offset = event.pos()

    # Обработка перетаскивания окна за title
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.window().move(self.window().pos() + event.pos() - self.offset)


class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UML editor")
        self.setWindowIcon(QtGui.QIcon("imgs/main_icon.png"))

        # Убираем стандартный заголовок окна
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Создание и установка кастомного заголовка
        self.custom_title_bar = CustomTitleBar()

        layout = QtWidgets.QVBoxLayout(self)

        # Добавление кастомного заголовка
        layout.addWidget(self.custom_title_bar)

        # Получаем размеры экрана для центрирования окна
        screen_geometry = QtWidgets.QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()

        # Устанавливаем начальный размер окна
        self.setFixedSize(300, 420)

        # Центрируем окно, учитывая его размеры
        window_size = self.size()
        self.move(screen_center.x() - window_size.width() // 2, screen_center.y() - window_size.height() // 2)

        self.user_data_folder = "user_data"
        os.makedirs(self.user_data_folder, exist_ok=True)

        # Создание элементов интерфейса
        self.logo_label = QtWidgets.QLabel(self)
        self.logo_pixmap = QtGui.QPixmap("imgs/ctuasologo_black")
        if not self.logo_pixmap.isNull():
            # Создаем прозрачный QPixmap
            transparent_pixmap = QtGui.QPixmap(self.logo_pixmap.size())
            transparent_pixmap.fill(QtCore.Qt.transparent)  # Устанавливаем прозрачный фон

            # Используем QPainter для установки прозрачности
            painter = QtGui.QPainter(transparent_pixmap)
            painter.setOpacity(0.5)  # Устанавливаем 50% прозрачности
            painter.drawPixmap(0, 0, self.logo_pixmap)  # Вставка исходного изображения
            painter.end()

            # Масштабируем изображение с сглаживанием
            self.logo_pixmap = transparent_pixmap.scaled(
                150, 150,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )

        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Добавление текста
        self.title_label = QtWidgets.QLabel("UML-Editor", self)
        font = QtGui.QFont("Arial", 20)  # Шрифт для текста
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Поля ввода
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.username_input.setMaxLength(20)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setMaxLength(20)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Регулярки полей ввода
        regex = QtCore.QRegExp("^[a-zA-Zа-яА-я0-9][a-zA-Zа-яА-я0-9_]*$")
        validator = QtGui.QRegExpValidator(regex, self.username_input)
        self.username_input.setValidator(validator)
        validator = QtGui.QRegExpValidator(regex, self.password_input)
        self.password_input.setValidator(validator)

        # Кнопки
        self.login_button = QtWidgets.QPushButton("Войти", self)
        self.register_button = QtWidgets.QPushButton("Зарегистрироваться", self)

        # Добавление виджетов в лейаут
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        # Связывание кнопок с методами
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        self.msg = QMessageBox() # Стандартное уведомелние, которое в дальнейшем будет кастомизироваться
        self.msg.setWindowIcon(QtGui.QIcon("imgs/main_icon.png"))
        # Применение дизайна
        self.setDesign()

    # Хэшируем пароль
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Вход
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user_file = os.path.join(self.user_data_folder, f"{username}.json")
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                user_data = json.load(f)

            # Если пароли совпадают
            if user_data.get("password") == self.hash_password(password):
                global global_start_time  # Получаем время начала работы
                global_start_time = user_data.get("start_time")
                self.msg.setWindowTitle("Успех")
                self.msg.setText(f"Добро пожаловать, {username}!")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.exec_()
                self.accept()  # Закрыть окно с результатом успешного входа
            else:
                self.msg.setWindowTitle("Ошибка")
                self.msg.setText("Неверный пароль!")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.exec_()
        else:
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText("Пользователь не найден!")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()

    # Регистрация
    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if len(username) > 3 and len(password) > 3:
            user_file = os.path.join(self.user_data_folder, f"{username}.json")

            if os.path.exists(user_file):
                self.msg.setWindowTitle("Ошибка")
                self.msg.setText("Пользователь с таким именем уже существует.")
                self.msg.setStandardButtons(QMessageBox.Ok)
                self.msg.exec_()
                return

            hashed_password = self.hash_password(password)
            user_data = {
                "username": username,
                "password": hashed_password,
                "start_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "end_time": None
            }

            global global_start_time  # Получаем время начала работы
            global_start_time = user_data.get("start_time")

            with open(user_file, "w") as f:
                json.dump(user_data, f)

            self.msg.setWindowTitle("Успех")
            self.msg.setText("Пользователь успешно зарегистрирован!")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()
            self.accept()  # Закрыть окно с результатом успешной регистрации
        else:
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText("Логин и пароль должны быть длиннее 3 символов.")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()

    def setDesign(self):
        self.setStyleSheet("""
        QWidget {
            font-family: 'Arial', sans-serif;
            font-size: 14px;
            color: #2f2f2f;
        }

        QLabel {
            font-size: 20px;
            font-weight: bold;
        }

        QLineEdit {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 6px;
            padding: 8px;
            font-family: 'Arial';
            font-size: 16px;
        }

        QPushButton {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(150, 150, 150);
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
            color: #2f2f2f;
        }

        QPushButton:hover {
            background-color: rgb(220, 220, 220);
            border: 1px solid rgb(100, 100, 100);
        }

        QPushButton:pressed {
            background-color: rgb(200, 200, 200);
        }
                           
""")
        self.msg.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.msg.setStyleSheet("""
    QMessageBox {
        background-color: #ffffff; /* Светлый фон */
        color: #2f2f2f; /* Основной цвет текста */
        border: 1px solid #dcdcdc;
        font-family: Arial, sans-serif;
        font-size: 18px;
        text-align: justify; /* Выравнивание текста */
        min-width: 400px;  /* Минимальная ширина окна */
        padding: 20px;
    }
    QMessageBox QLabel {
        color: #333333;
        font-size: 18px;
        font-weight: normal; /* Стандартный вес текста */
        padding: 10px 0px; /* Отступы сверху и снизу */
    }
    QMessageBox QPushButton {
        background-color: #f0f0f0;
        border: 1px solid #b0b0b0;
        border-radius: 6px; /* Округлые углы только для кнопок */
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        color: #2f2f2f; /* Темный текст на кнопках */
        margin: 5px;
    }
    QMessageBox QPushButton:hover {
        background-color: #e0e0e0; /* Подсветка при наведении */
        border: 1px solid #a0a0a0;
    }
    QMessageBox QPushButton:pressed {
        background-color: #d0d0d0; /* при нажатии */
    }
    QMessageBox QFrame {
        background-color: transparent;
    }
    QMessageBox QIcon {
        margin-right: 10px; /* Отступ иконки от текста (Если кто захочет вставить иконку)*/
    }
""")


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(300, 300, 600, 400)

        # Основной макет диалога настроек
        main_layout = QHBoxLayout(self)

        # Левый список разделов настроек
        self.section_list = QListWidget()
        self.section_list.addItems(["Общие","Сохранение"])
        self.section_list.currentRowChanged.connect(self.display_section)

        # Основная область для настройки выбранного раздела
        self.settings_stack = QStackedWidget()

        # Добавляем страницы для каждого раздела
        self.settings_stack.addWidget(self.create_general_settings())
        self.settings_stack.addWidget(self.create_save_settings())

        # Добавляем виджеты в основной макет
        main_layout.addWidget(self.section_list, 1)  # Список занимает 1 часть
        main_layout.addWidget(self.settings_stack, 3)  # Детальные настройки - 3 части

        self.setLayout(main_layout)

    def create_general_settings(self):
        """Создаем страницу для общих настроек."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Общие настройки"))
        layout.addWidget(QLabel("В разработке"))
        return page

    def create_save_settings(self):
        """Создаем страницу для настроек сохранения."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Настройки сохранения"))
        # Чекбокс для сохранения в режиме "Только просмотр"
        readonly_checkbox = QCheckBox("Сохранять в режиме 'Только просмотр'")
        readonly_checkbox.setChecked(False)  # По умолчанию выключен
        
        # Добавляем элементы в макет
        layout.addWidget(readonly_checkbox)
        return page

    def display_section(self, index):
        self.settings_stack.setCurrentIndex(index)

class Ui_MainWindow(QtWidgets.QMainWindow):
    time_updated = pyqtSignal(str, str, str)  # Создаем сигнал с параметром типа str для передачи запущенного времени
    update_last_timeSW = pyqtSignal(str, str, str)  # Создаем сигнал для передачи последнего значения времени
    count_objectS = pyqtSignal(int) # Создаем сигнал о подсчете количества объектов на сцене для отображения его в статистике
    user_actions = pyqtSignal(str, int, str, str, str, str, dict) # Создаем сигнал который учитывает дейсвтия пользователя на сцене для обновления информации на окне статистики


    def __init__(self):
        super().__init__()
        self.label_x_y = QtWidgets.QLabel(self)
        self.label_x_y.setText("(0, 0)")
        self.label_x_y.setAlignment(QtCore.Qt.AlignCenter)

        self.graphicsView = My_GraphicsView(self.label_x_y)
        self.graphicsView.setMouseTracking(True)
        self.username = global_username
        self.start_time = global_start_time
        # global GLOBAL_USERNAME
        # self.username = GLOBAL_USERNAME
        
        
        

        
    @pyqtSlot(str)   
    def set_username(self, username):
        self.username = username

    def setupUi(self, MainWindow):
        #self.username = username
        #print(self.username)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ToolBarBox = QtWidgets.QFrame(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.ToolBarBox.setFont(font)

        self.ToolBarBox.setObjectName("ToolBarBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.ToolBarBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        
        # Создание QLabel и добавление в gridLayout
        self.button = DraggableButton("Decision", self, self.ToolBarBox)
        self.button.setIconSize(QtCore.QSize(100, 100))  # Установка размера иконки (при необходимости)
        self.button.setObjectName("button")
        self.gridLayout.addWidget(self.button, 0, 0, 1, 1)
        self.button.setStyleSheet(""" QPushButton {
            border:none;                      }""")

        # startstate.png
        self.button_2 = DraggableButton("StartEvent", self, self.ToolBarBox)
        self.button_2.setIconSize(QtCore.QSize(100, 100))
        self.button_2.setObjectName("button_2")
        self.gridLayout.addWidget(self.button_2, 0, 1, 1, 1)
        self.button_2.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # finalstate.png
        self.button_3 = DraggableButton("EndEvent", self, self.ToolBarBox)
        self.button_3.setIconSize(QtCore.QSize(100, 100))
        self.button_3.setObjectName("button_3")
        self.gridLayout.addWidget(self.button_3, 0, 2, 1, 1)
        self.button_3.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Horizontal
        self.button_4 = DraggableButton("Splitter_Merge_Horizontal", self, self.ToolBarBox)
        self.button_4.setIconSize(QtCore.QSize(100, 100))
        self.button_4.setObjectName("button_4")
        self.gridLayout.addWidget(self.button_4, 1, 1, 1, 1)
        self.button_4.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Signal-sending.png
        self.button_5 = DraggableButton("SignalSending", self, self.ToolBarBox)
        self.button_5.setIconSize(QtCore.QSize(100, 100))
        self.button_5.setObjectName("button_5")
        self.gridLayout.addWidget(self.button_5, 2, 0, 1, 1)
        self.button_5.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Signal-receipt.png
        self.button_6 = DraggableButton("SignalReceipt", self, self.ToolBarBox)
        self.button_6.setIconSize(QtCore.QSize(100, 100))
        self.button_6.setObjectName("button_6")
        self.gridLayout.addWidget(self.button_6, 2, 1, 1, 1)
        self.button_6.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")


        # arrowsolid.png
        self.button_7 = DraggableButton("Text_Edit", self, self.ToolBarBox)
        self.button_7.setIconSize(QtCore.QSize(100, 100))
        self.button_7.setObjectName("button_7")
        self.gridLayout.addWidget(self.button_7, 2, 2, 1, 1)
        self.button_7.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Vertical
        self.button_8 = DraggableButton("Splitter_Merge_Vertical", self, self.ToolBarBox)
        self.button_8.setIconSize(QtCore.QSize(100, 100))
        self.button_8.setObjectName("button_8")
        self.gridLayout.addWidget(self.button_8, 1, 0, 1, 1)
        self.button_8.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")


        # ativestate.png
        self.button_9 = DraggableButton("ActiveState", self, self.ToolBarBox)
        self.button_9.setIconSize(QtCore.QSize(100, 100))
        self.button_9.setObjectName("button_9")
        self.gridLayout.addWidget(self.button_9, 1, 2, 1, 1)
        self.button_9.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.ToolBarBox)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_6.addWidget(self.graphicsView, 0, 0, 1, 1)
        # Добавление QLabel с изображением
        self.logoLabel = QtWidgets.QLabel(self.centralwidget)
        self.logoLabel.setObjectName("logoLabel")
        self.logoLabel.setMinimumSize(QtCore.QSize(100, 100))  # Минимальный размер
        self.logoLabel.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)  # Центрирование изображения
        
        # Загрузка изображения
        pixmap = QtGui.QPixmap("imgs/ctuasologo_black")
        if not pixmap.isNull():
            transparent_pixmap = QPixmap(pixmap.size())
            transparent_pixmap.fill(QtGui.QColor(0, 0, 0, 0))  # Прозрачный фон

            painter = QPainter(transparent_pixmap)
            painter.setOpacity(0.5)  # Устанавливаем 50% прозрачности
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            # Масштабируем прозрачное изображение
            scaled_pixmap = transparent_pixmap.scaled(
                150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )

            # Устанавливаем изображение в QLabel
            self.logoLabel.setPixmap(scaled_pixmap)
        else:
            self.logoLabel.setText("Логотип\nне найден")
        
        self.gridLayout_6.addWidget(self.logoLabel, 0, 1, 1, 1)  # Логотип справа


        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        #self.gridLayout_6.addWidget(self.frame, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.label_x_y = QtWidgets.QLabel(MainWindow)
        self.label_x_y.setObjectName("label_x_y")
        # self.label_x_y.setAlignment(QtCore.Qt.AlignRight)
        self.label_x_y.setStyleSheet("""
QLabel {
            color: gray;                         }""")
        self.label_x_y.setText("(0, 0)")
        self.label_x_y.setAlignment(QtCore.Qt.AlignLeft)
        self.gridLayout_2.addWidget(self.label_x_y, 1, 1, 1, 1)


        #Настройка главного меню
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 18))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_insert = QtWidgets.QMenu(self.menubar)
        self.menu_insert.setObjectName("menu_insert")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")

        #Тестовое меню для таймера
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")

        #Меню Окна
        self.menu_show_panel = QtWidgets.QMenu(self.menubar)
        self.menu_show_panel.setObjectName("menu_show_panel")

        #Меню Помощь
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")


        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        # self.action_PNG = QtWidgets.QAction(MainWindow)
        # self.action_PNG.setObjectName("action_PNG")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")

        self.action_settings = QtWidgets.QAction(MainWindow)
        self.action_settings.setObjectName("action_settings")

        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
        self.action_add_image = QtWidgets.QAction(MainWindow)
        self.action_add_image.setObjectName("action_add_image")
        self.action_Statystics = QtWidgets.QAction(MainWindow)
        self.action_Statystics.setObjectName("action_Statystics")

        #Тестовые вкладки для таймера
        self.action_time_start = QtWidgets.QAction(MainWindow)
        self.action_time_start.setObjectName("action_time_start")
        self.action_time_stop = QtWidgets.QAction(MainWindow)
        self.action_time_stop.setObjectName("action_time_stop")
        self.action_time_reset = QtWidgets.QAction(MainWindow)
        self.action_time_reset.setObjectName("action_time_reset")

        #Вкладки показа панелий
        self.action_edit_panel = QtWidgets.QAction(MainWindow)
        self.action_edit_panel.setObjectName("action_edit_panel")
        self.action_object_panel = QtWidgets.QAction(MainWindow)
        self.action_object_panel.setObjectName("action_object_panel")
        self.action_Toolbar = QtWidgets.QAction(MainWindow)
        self.action_Toolbar.setObjectName("action_Toolbar")

        # Подключаем действие для запуска окна статистики
        self.action_Statystics.triggered.connect(self.show_static_widget)

        self.menu.addAction(self.action_4)
        self.menu.addAction(self.action)
        self.menu.addSeparator()
        self.menu.addAction(self.action_2)
        self.menu.addAction(self.action_3)
        self.menu.addSeparator()
        # self.menu.addAction(self.action_PNG)
        self.menu.addAction(self.action_settings)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)
        self.menu_insert.addAction(self.action_add_image)
        self.menu_2.addAction(self.action_Statystics)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_insert.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_show_panel.menuAction())
        #self.menubar.addAction(self.menu_help)
        # Создаем действие для пункта "Помощь"
        self.action_help = QAction("Помощь", self)
        
        # Добавляем действие в менюбар
        self.menubar.addAction(self.action_help)

        #Панели
        self.menu_show_panel.addAction(self.action_edit_panel)
        self.menu_show_panel.addAction(self.action_object_panel)
        self.menu_show_panel.addAction(self.action_Toolbar)


        self.action_edit_panel.triggered.connect(self.show_edit_panel)
        self.action_object_panel.triggered.connect(self.show_object_panel)
        self.action_Toolbar.triggered.connect(self.show_toolbar)
        # self.menubar.addAction(self.menu_3.menuAction()) #Тестовое меню таймера

        self.action_2.triggered.connect(self.save_to_file)
        self.action_3.triggered.connect(self.save_as)
        self.action_4.triggered.connect(self.create_new)
        self.action.triggered.connect(self.open_file)
        self.action_settings.triggered.connect(self.open_settings)
        self.action_exit.triggered.connect(self.close_application)

        self.action_add_image.triggered.connect(self.insert_image)

        # Связываем сигнал triggered с методом show_help
        self.action_help.triggered.connect(self.show_help)
        
        self.help_window = None  # Окно помощи создается при первом вызове


        # Создаём невидимый QLabel для записи времени
        self.Start_Time = QtWidgets.QLineEdit(self.centralwidget)
        self.Start_Time.setGeometry(QtCore.QRect(100, 100, 200, 50))  # Устанавливаем размер и позицию
        self.Start_Time.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
        self.Start_Time.setText("00:00:00")  # Устанавливаем начальное значение времени
        self.Start_Time.setReadOnly(True)


        #Таймер
        global global_start_time # Глобальная переменная для получения даты начала работы

        buffer_date, buffer_time = global_start_time.split() # БУферные переменные для передачи данных и разбиение строки
        #Присваиваем полученные данные
        self.today = buffer_date
        self.time_now = buffer_time
        # Настраиваем второй таймер для обновления времени каждую секунду
        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.increment_time)  # Соединяем таймер с функцией обновления времени
        self.timer_2.start(1000)  # Запускаем таймер с интервалом в 1 секунду

        #Инициализируем переменные для секундомера
        self.running = False
        current_time_now = QTime.currentTime()
        # Преобразуем строку buffer_time в объект QTime
        buffer_time_obj = QTime()
        buffer_time_obj.setHMS(*map(int, buffer_time.split(":")))
        # Вычисляем разницу в секундах
        elapsed_seconds = current_time_now.secsTo(buffer_time_obj)
        # Преобразуем разницу в формате HH:MM:SS
        self.elapsed_time = QTime(0, 0).addSecs(abs(elapsed_seconds))

        self.timer = QTimer()

        self.last_time = self.Start_Time.text() # Изначальное значение времени
        self.Start_Time.setVisible(False) #По умолчанию всегда невиден
        self.timer.timeout.connect(self.update_time)

        self.today_uptadet = self.today
        self.time_now_uptadet = self.time_now

        self.running_inaction = False
        self.timer_inaction = QTimer()
        self.elapsed_Time_inaction = QTime(0, 0)


        # self.timer_inaction.timeout.connect(self.update_time)

        self.start()

        #Второй таймер для остановки основного таймера если пользователь бездействует
        self.Time_inaction = QtWidgets.QLineEdit(self.centralwidget)
        self.Time_inaction.setGeometry(QtCore.QRect(200, 200, 200, 50))  # Устанавливаем размер и позицию
        self.Time_inaction.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
        self.Time_inaction.setText("00:00:00")  # Устанавливаем начальное значение времени
        self.Time_inaction.setReadOnly(True)
        self.Time_inaction.setVisible(False) #По умолчанию всегда невиден



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



        # Кнопки тулбара
        self.button.clicked.connect(self.draw_diamond)
        self.button_2.clicked.connect(self.draw_circle)
        self.button_3.clicked.connect(self.draw_circle_2)
        self.button_9.clicked.connect(self.draw_rounded_rectangle)
        self.button_5.clicked.connect(self.draw_pentagon_signal)
        self.button_6.clicked.connect(self.draw_pentagon_reverse)
        self.button_8.clicked.connect(self.draw_splitter_merge_v)
        self.button_4.clicked.connect(self.draw_splitter_merge_h)
        self.button_7.clicked.connect(self.add_text)

        #Проверка превышение количества объектов на сцене
        self.button.clicked.connect(self.message_overcrowed_objectS)
        self.button_2.clicked.connect(self.message_overcrowed_objectS)
        self.button_3.clicked.connect(self.message_overcrowed_objectS)
        self.button_9.clicked.connect(self.message_overcrowed_objectS)
        self.button_5.clicked.connect(self.message_overcrowed_objectS)
        self.button_6.clicked.connect(self.message_overcrowed_objectS)
        self.button_8.clicked.connect(self.message_overcrowed_objectS)
        self.button_4.clicked.connect(self.message_overcrowed_objectS)
        self.button_7.clicked.connect(self.message_overcrowed_objectS)
        self.action_add_image.triggered.connect(self.message_overcrowed_objectS)

        

        #Подсказки с горячими клавишами на тулбаре
        self.button.setToolTip("Decision - '1'")
        self.button_2.setToolTip("Start event - '2'")
        self.button_3.setToolTip("End event - '3'")
        self.button_8.setToolTip("Splitter/Merge вертикальный - '4'")
        self.button_4.setToolTip("Splitter/Merge горизонатльный - '5'")
        self.button_9.setToolTip("Active state - '6'")
        self.button_5.setToolTip("Sending signal - '7'")
        self.button_6.setToolTip("Signal receipt - '8'")
        self.button_7.setToolTip("Текстовое поле - '9'")


        self.msg = QMessageBox()
        # self.msg.setIconPixmap(QPixmap("imgs/main_icon.png"))

        self.objectS_ = []
        self.graphicsView.setFocus()  # Устанавливаем фокус на graphicsView, чтобы горячие клавиши срабатывали через QShortcut
        self.connect_objectS = QShortcut(QKeySequence("Q"), self.graphicsView)
        self.connect_objectS.activated.connect(self.add_edge)

        self.connect_objectS = QShortcut(QKeySequence("delete"), self.graphicsView)
        self.connect_objectS.activated.connect(self.delete_selected_item)

        self.connect_objectS = QShortcut(QKeySequence("Ctrl+A"), self.graphicsView)
        self.connect_objectS.activated.connect(self.select_all_item)

        self.connect_objectS = QShortcut(QKeySequence("Ctrl+D"), self.graphicsView)
        self.connect_objectS.activated.connect(self.duplicate_selected_item)

        self.connect_objectS = QShortcut(QKeySequence("1"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_diamond)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("2"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_circle)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("3"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_circle_2)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("4"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_splitter_merge_v)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("5"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_splitter_merge_h)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("6"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_rounded_rectangle)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("7"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_pentagon_signal)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("8"), self.graphicsView)
        self.connect_objectS.activated.connect(self.draw_pentagon_reverse)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("9"), self.graphicsView)
        self.connect_objectS.activated.connect(self.add_text)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("0"), self.graphicsView)
        self.connect_objectS.activated.connect(self.insert_image)
        self.connect_objectS.activated.connect(self.message_overcrowed_objectS)

        self.connect_objectS = QShortcut(QKeySequence("Ctrl+S"), self.graphicsView)
        self.connect_objectS.activated.connect(self.save_to_file)
        
        self.connect_objectS = QShortcut(QKeySequence("Ctrl+N"), self.graphicsView)
        self.connect_objectS.activated.connect(self.create_new)
        
        self.connect_objectS = QShortcut(QKeySequence("Ctrl+M"), self.graphicsView)
        self.connect_objectS.activated.connect(self.show_static_widget)

        self.connect_objectS = QShortcut(QKeySequence("Alt+T"), self.graphicsView)
        self.connect_objectS.activated.connect(self.show_toolbar)

        self.connect_objectS = QShortcut(QKeySequence("Alt+O"), self.graphicsView)
        self.connect_objectS.activated.connect(self.show_object_panel)

        self.connect_objectS = QShortcut(QKeySequence("Alt+E"), self.graphicsView)
        self.connect_objectS.activated.connect(self.show_edit_panel)
        # self.connect_objectS = QShortcut(QKeySequence("T"), self.graphicsView)
        # self.connect_objectS.activated.connect(self.disconnect_nodes)


        self.user_ = User(self.username, 0, self.start_time, self.get_time_for_user(self.last_time))
        self.user_.add_action("Создана диаграмма UML", self.start_time)
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)


        self.scene_ = My_GraphicsScene(self, self.objectS_, self.user_, self.label_x_y)
        self.graphicsView.setScene(self.scene_)  # Устанавливаем сцену в QGraphicsView

        # Подключение сетики
        self.connect_objectS = QShortcut(QKeySequence("G"), self.graphicsView)
        self.connect_objectS.activated.connect(self.scene_.toggle_grid)

        self.editing_dock = QtWidgets.QDockWidget("Панель редактирования", MainWindow)
        self.editing_dock.setObjectName("editing_dock")
        editing_widget = QtWidgets.QWidget()
        self.editing_dock.setWidget(editing_widget)
        self.editing_dock.setFloating(True)  # Устанавливаем состояние "вытянутого" окна
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.editing_dock)
        self.editing_dock.setVisible(True)
        self.on_selection_changed()

        self.object_list_dock = QtWidgets.QDockWidget("Список объектов", MainWindow)
        self.object_list_dock.setObjectName("object_list_dock")

        self.dock_widget = QtWidgets.QDockWidget("Тулбар", MainWindow)
        self.dock_widget.setWidget(self.ToolBarBox)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        self.dock_widget.setVisible(True)

        object_list_widget = QtWidgets.QListWidget()
        self.object_list_widget = object_list_widget
        self.object_list_dock.setWidget(object_list_widget)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.object_list_dock)
        self.object_list_widget.itemClicked.connect(self.on_object_selected)
        self.populate_object_list()
        self.object_list_widget.itemClicked.connect(self.object_panel_on_item)

        self.setDesigh(MainWindow)

    def show_toolbar(self):
        self.reset_inaction()
        self.dock_widget.setVisible(True)

    def show_edit_panel(self):
        self.reset_inaction()
        self.editing_dock.setVisible(True)

    def show_object_panel(self):
        self.reset_inaction()
        self.object_list_dock.setVisible(True)

    # Выделение объекта и вызов панели редактирование для него через виджет "Список элементов"
    def object_panel_on_item(self):
        # Сначало снимаем выделение со всех элементов
        for all_item in self.scene_.items():
            # Проверяем может ли элемент выделяться
            if isinstance(all_item, QtWidgets.QGraphicsItem):
                all_item.setSelected(False) # Снимаем выделение

        current_row = self.object_list_widget.currentRow()
        item = self.objectS_[current_row]
        item.setSelected(True) # Выделяем конкретный элемент
        self.show_editing_panel(item) #Показываем информацию о выделенном элементе в окне редактирования

    def object_panel_select(self, i_item):
        self.object_list_widget.setCurrentRow(i_item)

    def populate_object_list(self):
        self.object_list_widget.clear()
        for index, item in enumerate(self.objectS_):
            list_item_text = f"#{item.unique_id}: {type(item).__name__}"
            list_item = QtWidgets.QListWidgetItem(list_item_text)
            self.object_list_widget.addItem(list_item)
            

    def open_settings(self):
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.exec_()


    def show_help(self):
        self.reset_inaction()
        if not self.help_window:
            self.help_window = HelpWindow()
        self.help_window.show()

    def on_object_selected(self, item):
        # Получаем объект, привязанный к элементу списка
        self.reset_inaction()
        selected_object = item.data(Qt.UserRole)
        if selected_object:
            # Снимаем выделение со всех объектов
            for obj in self.objectS_:
                obj.setSelected(False)  # Снимаем выделение

            # Выделяем выбранный объект
            selected_object.setSelected(True)

            # Центрируем сцену на выделенном объекте (опционально)
            if hasattr(self.scene_view, "centerOn"):
                self.scene_view.centerOn(selected_object)

            print(f"Выбран объект: {type(selected_object).__name__}")

        

    def on_selection_changed(self):
        self.editing_dock.setVisible(False)

    def show_editing_panel(self, item):
        self.reset_inaction()
        # Создание и отображение панели редактирования для выбранного объекта
        self.editing_panel = EditingPanel(item, self)
        self.editing_dock.setWidget(self.editing_panel)
        self.editing_dock.setVisible(True)

        # Обновление панели с координатами
            # Универсальная обработка центра объекта
        if isinstance(item, QtWidgets.QGraphicsPolygonItem):
            # Центр полигона (Splitter_Merge, SignalSending и SignalReceip)
            polygon = item.polygon()
            x = sum(point.x() for point in polygon) / len(polygon)
            y = sum(point.y() for point in polygon) / len(polygon)
            local_center = QtCore.QPointF(x, y)
        elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
            # Центр круга
            local_center = item.rect().center()
        elif isinstance(item, QtWidgets.QGraphicsRectItem):
            # Центр прямоугольника
            local_center = item.rect().center()
        elif isinstance(item, QtWidgets.QGraphicsTextItem):
            # Центр текста
            local_center = item.boundingRect().center()
        elif isinstance(item, QtWidgets.QGraphicsPixmapItem):
            # Центр изображения
            local_center = item.pixmap().rect().center()
        else:
            print(f"Неизвестный тип объекта: {type(item).__name__}")
            return

        # Преобразуем центр в глобальные координаты сцены
        global_center = item.mapToScene(local_center)
        view_center = self.scene_.views()[0].mapToGlobal(self.scene_.views()[0].mapFromScene(global_center))

        # Смещение для панели относительно объекта
        offset_x, offset_y = 30, 30
        dock_x = view_center.x() + offset_x
        dock_y = view_center.y() + offset_y

        # Устанавливаем позицию панели
        self.editing_dock.move(dock_x, dock_y)

        # Передаем координаты центра в панель редактирования
        self.scene_.coordinates_updated.emit(global_center.x(), global_center.y())


    def update_coordinates_in_panel(self, x, y):
       # обновление координат в панели редактирования
        if self.editing_panel:
            self.editing_panel.update_coordinates(x, y)



    # Быстрое сохранение в папку saves
    def save_to_file(self, filepath=None):
        self.reset_inaction()
        # Получаем директорию, где находится исполняемый файл
        base_dir = os.path.dirname(os.path.abspath(__file__))
        saves_dir = os.path.join(base_dir, "saves")

        # Создаём папку "saves", если её нет
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)

        # Если путь не задан, создаём имя файла по умолчанию
        if not filepath:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Временная метка
            filepath = os.path.join(saves_dir, f"diagram_{current_time}.chep")

        data = {"items": [], "arrows": []}
        elements = {}

        # Сохраняем элементы, пропуская стрелки
        for item in self.scene_.items():
            if isinstance(item, QtWidgets.QGraphicsItem) and not isinstance(item, Arrow) and not isinstance(item, QGraphicsEllipseItem):
                item_data = self.serialize_item(item)
                data["items"].append(item_data)  # Добавляем элемент в items
                elements[item.unique_id] = item  # Сохраняем элемент по уникальному идентификатору

            if isinstance(item, QGraphicsEllipseItem):
                item_data = self.serialize_item(item)
                data["items"].append(item_data)  # Добавляем элемент в items
                

        # Сохраняем стрелки отдельно через их id
        for item in self.scene_.items():
            if isinstance(item, Arrow):
                start_node_id = item.node1.unique_id   # Получаем id начального узла
                end_node_id = item.node2.unique_id     # Получаем id конечного узла
                dots = item.intermediate_points        # Получаем точки изгиба
                line_type = item.line_type             # Получаем тип начертания линии
                print(QtGui.QColor(item.color).name())
                if isinstance(item.color, QtGui.QColor):
                    color = item.color.name()  # HEX-строка
                else:
                    color = "#8B0000"  # Дефолтный цвет
                
                line_width = item.pen_width            # Получаем толщину линии
                right_arrow = item.right_arrow_enabled # Получаем флаг правого наконечника
                left_arrow = item.left_arrow_enabled   # Получаем флаг левого наконечника
                show_points = item.show_points         # Получаем флаг видимости точек

                        # Преобразуем intermediate_points в сериализуемый формат
                dots = [[point.x(), point.y()] for point in item.intermediate_points]

                data["arrows"].append({
                    "start_node_id": start_node_id, # Начало стрелки
                    "end_node_id": end_node_id, # Конец стрелки
                    "dots": dots, # Точки изгиба
                    "line_type": line_type, # Тип начертания линии
                    "color": color,  # Сохраняем цвет как строку в формате HEX
                    "width": line_width, # Толщина линии
                    "right_arrow": right_arrow, # Правый наконечник
                    "left_arrow": left_arrow, # Левый наконечник
                    "show_points": show_points, # Видимость точек

                })

        try:
            # Сохраняем данные в файл
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print("Файл сохранён:", filepath)
            self.msg.setWindowTitle("Сохранение")
            self.msg.setText(f"Файл успешно сохранён в:\n{filepath}")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.msg.exec_()
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText(f"Не удалось сохранить файл: {e}")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.msg.exec_()

    # Сохранение с пользовательским названием в конкретное место
    def save_as(self, filepath=None):
        self.reset_inaction()
        if not filepath:  # Если путь не задан, запрашиваем его у пользователя
            options = QtWidgets.QFileDialog.Options()
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "CHEP Files (*.chep);;All Files (*)", options=options
            )
            if not filepath:
                return

        # Массивы для хранения данных
        data = {"items": [], "arrows": []} 
        elements = {}

        # Сохраняем элементы, пропуская стрелки
        for item in self.scene_.items():
            if isinstance(item, QtWidgets.QGraphicsItem) and not isinstance(item, Arrow) and not isinstance(item, QGraphicsEllipseItem):
                item_data = self.serialize_item(item)
                data["items"].append(item_data)  # Добавляем элемент в items
                elements[item.unique_id] = item  # Сохраняем элемент по уникальному идентификатору

            if isinstance(item, QGraphicsEllipseItem):
                item_data = self.serialize_item(item)
                data["items"].append(item_data)  # Добавляем элемент в items
                

        # Сохраняем стрелки отдельно через их id
        for item in self.scene_.items():
            if isinstance(item, Arrow):
                start_node_id = item.node1.unique_id  # Получаем id начального узла
                end_node_id = item.node2.unique_id    # Получаем id конечного узла
                dots = item.intermediate_points
                line_type = item.line_type            # Получаем тип начертания линии
                if isinstance(item.color, QtGui.QColor):
                    color = item.color.name()  # HEX-строка
                else:
                    color = "#8B0000"  # Дефолтный цвет
                line_width = item.pen_width           # Получаем толщину линии
                right_arrow = item.right_arrow_enabled # Получаем флаг правого наконечника
                left_arrow = item.left_arrow_enabled   # Получаем флаг левого наконечника
                show_points = item.show_points         # Получаем флаг видимости точек

                        # Преобразуем intermediate_points в сериализуемый формат
                dots = [[point.x(), point.y()] for point in item.intermediate_points]

                data["arrows"].append({
                    "start_node_id": start_node_id, # Начало стрелки
                    "end_node_id": end_node_id, # Конец стрелки
                    "dots": dots, # Точки изгиба
                    "line_type": line_type, # Тип начертания линии
                    "color": color,  # Сохраняем цвет как строку в формате HEX
                    "width": line_width, # Толщина линии
                    "right_arrow": right_arrow, # Правый наконечник
                    "left_arrow": left_arrow, # Левый наконечник
                    "show_points": show_points, # Видимость точек
                })


        try:
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print("Файл сохранён:", filepath)
            self.msg.setWindowTitle("Сохранение")
            self.msg.setText(f"Файл успешно сохранён в:\n{filepath}")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.msg.exec_()
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText(f"Не удалось сохранить файл: {e}")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.msg.exec_()

    # Открытие файла
    def open_file(self):
        self.reset_inaction()

        options = QtWidgets.QFileDialog.Options()
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "CHEP Files (*.chep);;All Files (*)", options=options
        )
        if not filepath:
            return

        try:
            with open(filepath, "r") as file:
                data = json.load(file)
            self.load_from_data(data)
            print("Файл открыт:", filepath)
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText(f"Не удалось открыть файл: {e}")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.No)
            self.msg.exec_()

    # Сериализация элементов для их дальнейшего сохранения
    def serialize_item(self, item):
        print('Вызвано')
        base_data = {
            "type": type(item).__name__,      # Тип элемента
            "position": (item.x(), item.y()), # Позиция элемента
            "size": None,                     # Размер (например, для Decision)
            "radius": None,                   # Радиус (например, для StartEvent и EndEvent)
            "inner_radius_ratio": None,       # Соотношение радиусов (EndEvent)
            "width": None,                    # Ширина (например, для ActiveState)
            "height": None,                   # Высота (например, для ActiveState)
            "text": None,                     # Текст (например, для ActiveState)
            "start_node": None,               # Начальная точка (для Arrow)
            "end_node": None,                 # Конечная точка (для Arrow)
            "color": None,                    # Цвет линии (для Arrow)
            "line_width": None,               # Толщина линии (для Arrow)
            "start_node": None,               # Начальная точка соединения (для Arrow)
            "end_node": None,                 # Конечная точка соединения (для Arrow)
            "color": None,                    # Цвет линии (для Arrow)
            "line_width": None,               # Ширина линии (для Arrow)
            "id": None,                       # Идентификатор
            "dots": None,                     # Флаги точек изгиба (для Arrow)
            "pixmap": None,                   # Изображение
            "opacity": None,                  # Прозрачность (для ImageItem)
            "rotation": None,                 # Положение (для Splitter_Merge)
            "direction": None,                # Направление (для сигналов)
        }

       
        # Заполняем структуру в зависимости от типа элемента
        if isinstance(item, Decision):  # Ромб
            print(QtGui.QColor(item.color).name())
            base_data["size"] = item.size
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()/ 2
            y = p_center.y() / 2
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id 
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет
            

        elif isinstance(item, StartEvent):  # Круг (начало)
            rect = item.rect()
            base_data["radius"] = rect.width() / 2
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y()
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет

        elif isinstance(item, EndEvent):  # Круг с внутренним кругом (конец)
            rect = item.rect()
            base_data["radius"] = rect.width() / 2
            base_data["inner_radius_ratio"] = item.inner_radius_ratio
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y()
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет

        elif isinstance(item, ActiveState):  # Прямоугольник с закругленными углами
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()
            base_data["radius"] = item.radius
            base_data["text"] = item.text_item.toPlainText() if hasattr(item, "text_item") else None
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x() - 50
            y = p_center.y() - 30
            print(x, y)
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет

        elif isinstance(item, SignalSending):  # Пентагон (сигнал отправки)
            rect = item.boundingRect()
            base_data["width"] = item.width
            base_data["height"] = item.height
            base_data["text"] = item.text_item.toPlainText() if hasattr(item, "text_item") else None
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x() - 15
            y = p_center.y() + 30
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет
            base_data["direction"] = item.trans

        elif isinstance(item, SignalReceipt):  # Пентагон (сигнал получения)
            rect = item.boundingRect()
            base_data["width"] = item.width
            base_data["height"] = item.height
            base_data["text"] = item.text_item.toPlainText() if hasattr(item, "text_item") else None
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y() + 30
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет

            base_data["direction"] = item.trans

        

        elif isinstance(item, QtWidgets.QGraphicsEllipseItem):  # Простой круг
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()

            # Обработка ImageItem
        elif isinstance(item, ImageItem):
            position = item.sceneBoundingRect()
            p_center = position.center()
            base_data["id"] = item.unique_id
            base_data["position"] = {"x": p_center.x(), "y": p_center.y()}
            base_data["type"] = "ImageItem"
            pixmap_bytes = QtCore.QByteArray()
            buffer = QtCore.QBuffer(pixmap_bytes)
            buffer.open(QtCore.QIODevice.WriteOnly)
            item.pixmap().save(buffer, "PNG")
            base_data["pixmap"] = pixmap_bytes.toBase64().data().decode("utf-8")
            base_data["opacity"] = item.opacity()

        elif isinstance(item, Text_Edit):
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x() - len(item.toPlainText()) * 5.5
            y = p_center.y()
            base_data["position"] = {"x": x , "y": y - 16}
            # rect = item.boundingRect()
            base_data["width"] = item.width
            base_data["height"] = item.height
            # rect = item.rect()
            base_data["id"] = item.unique_id
            # base_data["position"] = {"x": item.x_center, "y": item.y_center}
            base_data["text"] = item.toPlainText()

        elif isinstance(item, Splitter_Merge):
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y()
            if item.rot == 0:
                base_data["position"] = {"x": x, "y": y + 10}
            if item.rot == 90:
                base_data["position"] = {"x": x - 10, "y": y}
            base_data["width"] = item.width
            base_data["height"] = item.height
            base_data["id"] = item.unique_id
            # base_data["position"] = {"x": item.center_x, "y": item.center_y}
            base_data["rotation"] = item.rot
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # HEX-строка
            else:
                base_data["color"] = QtGui.QColor(item.color).name()  # Дефолтный цвет



        return base_data

    # Закрытие приложения
    def close_application(self):
        self.close()

    # Обработка кнопки 'Выход'
    def closeEvent(self, event):

        self.reset_inaction()
        print('Вызвано')

        # Если диаграмма не пустая
        if len(self.objectS_) > 0:
            self.msg.setWindowTitle("Выход")
            self.msg.setText("Вы уверены, что хотите выйти? Изменения не будут сохранены.")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            self.msg.setDefaultButton(QtWidgets.QMessageBox.No)

            # Отображение окна и получение ответа
            reply = self.msg.exec_()

            if reply == QtWidgets.QMessageBox.Yes:
                print('egre')
                QtWidgets.QApplication.quit()
            else:
                event.ignore()
        else:
            QtWidgets.QApplication.quit()
    
    def message_overcrowed_objectS(self):
        self.reset_inaction()
        if len(self.objectS_) > 50:
            self.reset_inaction() #Сбрасыем второй таймер
            self.count_objectS.emit(len(self.objectS_) - 1)
            self.scene_.removeItem(self.objectS_[len(self.objectS_) - 1])
            del self.objectS_[len(self.objectS_) - 1]
            self.populate_object_list()
            self.msg.setIcon(QMessageBox.Information)
            self.msg.setText("Превышено максимальное значение элементов")
            self.msg.setWindowTitle("Предупреждение")
            self.msg.setStandardButtons(QMessageBox.Ok )
            self.user_.pop_action()
            self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)
            self.msg.exec()

    # def message_arrow(self):
    #     self.msg = QMessageBox()
    #     self.msg.setIcon(QMessageBox.Information)
    #     self.msg.setText("Стрелка уже существует между выбранными элементами")
    #     self.msg.setWindowTitle("Предупреждение")
    #     self.msg.setStandardButtons(QMessageBox.Ok )


    # def add_text_edit(self, x, y, width, height, text="Введите текст"):
    #     text_item = Text_Edit(x, y, width, height, text)
    #
    #     text_item.setFlags(
    #         QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)  # Позволяет перемещать и выделять
    #     self.scene_.addItem(text_item)  # Добавляем текстовое поле на сцену

    def add_text(self):
        self.reset_inaction()
        text_item = Text_Edit(0, 0, 100, 30, "Текст")
        self.scene_.addItem(text_item)
        self.objectS_.append(text_item)
        self.populate_object_list()
        self.count_objectS.emit(len(self.objectS_))
        self.user_.add_action(f"Добавлен элемент '{text_item.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_diamond(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра и размер ромба
        x, y, size = 0, 0, 50  # Пример координат и размера
        diamond = Decision(x, y, size)
        self.scene_.addItem(diamond)  # Добавляем ромб на сцену


        self.objectS_.append(diamond)
        self.populate_object_list()

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{diamond.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)
        
        

    def draw_circle(self):
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        self.reset_inaction() #Сбрасыем второй таймер
        x, y, radius = 0, 0, 30  # Пример: рисуем круг в центре с радиусом 50
        circle = StartEvent(x, y, radius)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)
        self.populate_object_list()

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{circle.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)
        # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_circle_2(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        x, y, radius, into_radius = 0, 0, 30, 0.5  # Пример: рисуем круг в центре с радиусом 50
        circle = EndEvent(x,y,radius, into_radius)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)
        self.populate_object_list()

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{circle.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)


    def draw_rounded_rectangle(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, width, height, radius = 0, 0, 100, 60, 15  # Пример координат, размера и радиуса
        rounded_rect = ActiveState(x, y, width, height, radius)
        self.scene_.addItem(rounded_rect)  # Добавляем закругленный прямоугольник на сцену

        self.objectS_.append(rounded_rect)
        self.populate_object_list()

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{rounded_rect.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)


    def draw_pentagon_signal(self):

        self.reset_inaction() #Сбрасыем второй таймер

        # self.reset_inaction() #Сбрасыем второй таймер
        pentagon = SignalSending(0, 0, 160, 60, "Справа")

        pentagon.reflect("Справа")
        self.scene_.addItem(pentagon)  # Добавляем закругленный прямоугольник на сцену
        self.objectS_.append(pentagon)
        self.populate_object_list()
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_pentagon_reverse(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # self.reset_inaction() #Сбрасыем второй таймер
        pentagon = SignalReceipt(0, 0, 180, 60, "Слева")

        pentagon.reflect("Слева")
        self.scene_.addItem(pentagon)
        self.objectS_.append(pentagon)
        self.populate_object_list()
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_splitter_merge_h(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y = 0, 0  # Пример координат, размера и радиуса
        stick = Splitter_Merge(x, y, 120, 40, 0)
        stick.setRotation(0)
        self.scene_.addItem(stick) 
        self.objectS_.append(stick)
        self.populate_object_list()
        self.user_.add_action(f"Добавлена конструкция Spliter_Merge'", self.get_current_Realtime())
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

    def draw_splitter_merge_v(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y = 0, 0  # Пример координат, размера и радиуса
        stick = Splitter_Merge(x, y, 120, 40, 90)
        stick.setRotation(90)
        self.scene_.addItem(stick) 
        self.objectS_.append(stick)
        self.populate_object_list()
        self.user_.add_action(f"Добавлена конструкция Spliter_Merge'", self.get_current_Realtime())
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))



    def add_edge(self):
        self.reset_inaction() #Сбрасыем второй таймер
        selected_nodes = [object_ for object_ in self.objectS_ if object_.isSelected()]
        # Обработка случая, когда пользователь хочет соединить более двух элементов
        if len(selected_nodes) > 2:
            self.msg.setWindowTitle('Внимание')
            self.msg.setText('Нельзя соединить более двух элементов одновременно.')
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()
        # Обработка случая, когда пользователь хочет соединить менее двух элементов
        if len(selected_nodes) < 2:
            self.msg.setWindowTitle('Внимание')
            self.msg.setText('Выберите два элемента для соединения.')
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.exec_()

        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes
            print(node1)

            # Проверяем, существует ли уже стрелка между node1 и node2
            for arrow in node1.arrows:
                if (arrow.node1 == node1 and arrow.node2 == node2) or (arrow.node1 == node2 and arrow.node2 == node1):
                    self.msg.setWindowTitle('Предупреждение')
                    self.msg.setText('Стрелка уже существует между выбранными элементами. Повторное соединение не возможно.')
                    self.msg.setStandardButtons(QMessageBox.Ok)
                    self.msg.exec_()
                    return # Принудительно прекращаем дальнейшие действия и избегаем повторного добавления

            # Создаем стрелку и привязываем её к выбранным узлам
            arrow = Arrow(node1, node2)
            arrow.setZValue(-1) # Стрелка всегда должна находится под объектами
            self.scene_.addItem(arrow)  # Добавляем стрелку на сцену

            # Привязываем стрелку к обоим узлам
            node1.add_arrow(arrow)
            node2.add_arrow(arrow)

            # Обновляем стрелку сразу после добавления
            arrow.update_arrow()  # Обновляем стрелку вручную, если нужно
            self.scene_.update()  # Перерисовываем сцену
            self.user_.add_action(f"Соединены '{node1.__class__.__name__}' и '{node2.__class__.__name__}'", self.get_current_Realtime())
    
    def select_all_item(self):
        self.reset_inaction()
        for item in self.scene_.items():
            # Проверяем может ли элемент выделяться
            if isinstance(item, QtWidgets.QGraphicsItem):
                item.setSelected(True)

    # Ненужный метод
    def disconnect_nodes(self, node1, node2):
        self.reset_inaction()
        if hasattr(node1, 'arrows') and hasattr(node2, 'arrows'):
            for arrow in node1.arrows[:]:
                if (arrow.node1 == node2 or arrow.node2 == node2) and arrow in node2.arrows:
                    self.user_.add_action(f"Рассоединены '{node1.__class__.__name__}' и '{node2.__class__.__name__}'", self.get_current_Realtime())
                    arrow.remove_arrow()
        self.scene_.update()


    def delete_selected_item(self):
        self.reset_inaction()  # Сбрасываем второй таймер
        selected_items = self.scene_.selectedItems()        

        for item in selected_items:
            if isinstance(item, Arrow):
                if item.scene():  # Проверяем, что стрелка все еще в сцене
                    item.remove_arrow()  # Удаляем стрелку
                self.on_selection_changed()

            if isinstance(item, (StartEvent, Decision, EndEvent, ActiveState, SignalSending, SignalReceipt, Splitter_Merge, ImageItem, Text_Edit)):
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    arrows_to_remove = list(item.arrows)  # Копируем список стрелок, чтобы избежать изменений во время итерации
                    for arrow in arrows_to_remove:
                        if arrow.scene():  # Проверяем, что стрелка все еще в сцене
                            self.scene_.removeItem(arrow)
                            # Удаляем стрелку из списка стрелок узла
                            item.arrows.remove(arrow)
                            del arrow
                    # del arrows_to_remove

                # Удаляем сам элемент из сцены
                self.scene_.removeItem(item)
                # Добавляем действие пользователя
                self.user_.add_action(f"Удален элемент '{item.__class__.__name__}'", self.get_current_Realtime())
                del item
                self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

        self.count_objectS.emit(len(self.objectS_))
        self.on_selection_changed()
        self.scene_.update()  # Перерисовываем сцену
        self.populate_object_list()
        del selected_items

    #Для панели редактирования
    def delete_specific_item(self, item):
        self.reset_inaction()
        if isinstance(item, (StartEvent, Decision, EndEvent, ActiveState, SignalSending, SignalReceipt, Splitter_Merge, ImageItem, Text_Edit)):

            if item in self.objectS_:
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    arrows_to_remove = list(item.arrows)
                    for arrow in arrows_to_remove:
                        if arrow.scene():
                            self.scene_.removeItem(arrow)
                            item.arrows.remove(arrow)
                            del arrow
                    del arrows_to_remove

                self.scene_.removeItem(item)
                self.user_.add_action(f"Удален элемент '{item.__class__.__name__}'", self.get_current_Realtime())
                self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work,
                                    next(reversed(self.user_.action_history)),
                                    next(reversed(self.user_.action_history.values())),
                                    self.user_.action_history)
                self.count_objectS.emit(len(self.objectS_))
                self.scene_.update()
                self.populate_object_list()
                self.on_selection_changed()
            else:
                print(f"Объект {item.__class__.__name__} отсутствует в objectS_")

    def duplicate_selected_item(self):
        selected_items = self.scene_.selectedItems()

        for item in selected_items:
            if isinstance(item, (StartEvent, Decision, EndEvent, ActiveState, SignalSending, SignalReceipt, Splitter_Merge, ImageItem, Text_Edit)):
                # Копируем свойства объекта
                new_item = item.clone()

                new_pos = item.scenePos() + QPointF(10, 10)
                new_item.setPos(new_pos)

                self.scene_.addItem(new_item)
                self.objectS_.append(new_item)

                if (len(self.objectS_)> 50):
                    self.message_overcrowed_objectS()

                #это для стрелочек. пока не работает
                if hasattr(new_item, 'arrows'):
                    new_item.arrows = []

                self.user_.add_action(f"Создан дубликат элемента '{item.__class__.__name__}'", self.get_current_Realtime())
                self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work,
                                    next(reversed(self.user_.action_history)),
                                    next(reversed(self.user_.action_history.values())),
                                    self.user_.action_history)

        self.count_objectS.emit(len(self.objectS_))
        self.scene_.update()
        self.populate_object_list()


    #Ниже 7 функции - реализация работы таймера

    def start(self):
        if not self.running:  # Запускаем таймер, только если он не запущен
            self.running = True
            self.timer.start(1000)  # Интервал 1000 мс (1 секунда)
            self.timer_2.start(1000)  # Запускаем таймер с интервалом в 1 секунду
            # self.timer_inaction(1000)
        # if not self.running_inaction:
            self.timer_inaction.start(1000)


    def stop(self):
        if self.running:  # Останавливаем таймер
            self.running = False
            self.timer.stop()
            self.timer_2.stop()
            self.last_time = self.Start_Time.text()  # Сохраняем текущее значение времени перед остановкой

            self.today_uptadet = self.get_current_Date()
            self.time_now_uptadet = self.get_current_Realtime()

            self.running_inaction = False
            # self.timer_inaction.stop()

            self.time_updated.emit(self.today_uptadet, self.last_time, self.time_now_uptadet)
            self.tray_icon.showMessage("Предупреждение", f"Работа приостановлена в {self.get_current_Realtime()}. Программа ожидает отклика пользователя", QSystemTrayIcon.MessageIcon.NoIcon, 1000000)

    def stop_inaction(self): #Остановка таймера бездействия (к примеру останавливате таймер)
        if self.running_inaction:     #когда пользователь вытаскивает элемент из тулбара
            self.running_inaction = False
            self.timer_inaction.stop()

    def reset(self):
        self.elapsed_time = QTime(0, 0)  # Сбрасываем время
        #self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)  # Увеличиваем время на 1 секунду
        time_str = self.elapsed_time.toString("hh:mm:ss")  # Преобразуем время в строку
        self.elapsed_Time_inaction = self.elapsed_Time_inaction.addSecs(1)
        time_str2 = self.elapsed_Time_inaction.toString("hh:mm:ss")
        self.Start_Time.setText(time_str)  # Обновляем отображение времени
        self.last_time = time_str  # Сохраняем последнее значение времени
        self.Time_inaction.setText(time_str2)

        if self.elapsed_Time_inaction == QTime(0, 1, 0):
            self.stop()
    
    def reset_inaction(self):
        self.elapsed_Time_inaction = QTime(0, 0)  # Сбрасываем время
        self.start()

    def get_current_Date(self):
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y")  # Возвращает текущую дату в формате "dd.mm.yyyy"
    
    # Возвращает сегодняшнее время
    def get_current_Realtime(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")  # Возвращает текущее время в формате "hh:mm:ss"

    def change_end_time(self):
        # curren_d = QDate.currentDate().addDays(10).toString("dd.MM.yyyy")
        date_now = self.get_current_Date()
        time_now = self.get_current_Realtime()
        l_time_sec = QDateTime.fromString(self.last_time, "HH:mm:ss").time().second()

        inc_time = QDateTime.fromString(time_now, "HH:mm:ss").addMSecs(l_time_sec).toString("HH:mm:ss")
        # curren_d = QDate.fromString(self.today, "dd.MM.yyyy").addDays(10).toString("dd.MM.yyyy")
        return f"{date_now} {inc_time}"

    
    def increment_time(self):
        # Логика обновления last_time, например, в формате HH:MM:SS

        hours, minutes, seconds = map(int, self.last_time.split(":"))
        seconds += 1
        if seconds >= 60:
            seconds = 0
            minutes += 1
        if minutes >= 60:
            minutes = 0
            hours += 1
        self.last_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.today_uptadet = self.get_current_Date()
        self.time_now_uptadet = self.get_current_Realtime()
        
        self.time_updated.emit(self.today_uptadet, self.last_time, self.time_now_uptadet)  # Отправляем обновленное значение
        self.get_time_for_user(self.last_time)

    def get_time_for_user(self, last_time):
        return last_time

    # Получение элемента ИЗ ПАМЯТИ по идентификатору
    def get_element_by_id(self, id):
        for item in self.objectS_: # Проходимся по массиву с объектами
            if item.unique_id == id:
                return item
        return None
    
    # Получение данных из открытого файла
    def load_from_data(self, data):
        self.reset_inaction()
        self.objectS_.clear() # Очистка массива с объектами
        self.scene_.clear() # Очистка сцены
        elements = {}  # Словарь для хранения элементов по их координатам

        # Проходимся по сохранению
        for item_data in data["items"]:
            item_type = item_data["type"] # Элемент
            position = item_data["position"] # Позиция

            # Создание объектов в зависимости от типа
            # Ромб
            if item_type == "Decision":
                size = item_data.get("size")  # Достаём "size" с умолчанием
                color = item_data.get("color", "#000000")

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию

                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                print(x, y)

                item = Decision(x, y, size, color=color)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)
                # Устанавливаем точную позицию
                item.setPos(x, y)

            # Элемент Начало диаграммы
            elif item_type == "StartEvent":
                radius = item_data.get("radius", 30)  # Достаём "radius" с умолчанием
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                color = item_data.get("color", "#000000")

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию
                item = StartEvent(x, y, radius, color=color)
                print('id now:', item.unique_id)
                item.unique_id = item_data.get("id")
                print('id after:', item.unique_id)
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Элемент Конец диаграммы
            elif item_type == "EndEvent":
                radius = item_data.get("radius", 30) # Радиус наружнего круга
                inner_radius_ratio = item_data.get("inner_radius_ratio", 0.5) # Радиус внутреннего круга
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                color = item_data.get("color", "#000000")

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию
                item = EndEvent(x, y, radius, inner_radius_ratio, color=color)
                item.unique_id = item_data.get("id")
                
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Прямоугольник с текстом
            elif item_type == "ActiveState":
                width = item_data.get("width", 100)
                height = item_data.get("height", 50)
                radius = item_data.get("radius", 10) # Радиус закругления углов
                text = item_data.get("text", "") # Текст
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                color = item_data.get("color", "#000000")

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию
                item = ActiveState(x, y, width, height, radius, color=color)
                item.unique_id = item_data.get("id")
                item.text_item.setPlainText(text)
                
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Отправка сигнала
            elif item_type == "SignalSending":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                text = item_data.get("text", "") # Текст
                x, y = position_data.get("x"), position_data.get("y")
                color = item_data.get("color", "#000000")
                trans = item_data.get("direction") # Направление

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию
                item = SignalSending(x, y, width, height, trans, color=color)
                item.unique_id = item_data.get("id")
                item.text_item.setPlainText(text)
                item.reflect(trans)
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Получение сигнала
            elif item_type == "SignalReceipt":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                text = item_data.get("text", "") # Текст
                x, y = position_data.get("x"), position_data.get("y")
                color = item_data.get("color", "#000000")
                trans = item_data.get("direction") # Направление стрелки

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию
                item = SignalReceipt(x, y, width, height, trans, color=color)

                item.unique_id = item_data.get("id")
                item.text_item.setPlainText(text)
                item.reflect(trans)
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Круг
            elif item_type == "QtWidgets.QGraphicsEllipseItem":
                width = item_data.get("width", 60)
                height = item_data.get("height", 60)
                rect = QRectF(-width / 2, -height / 2, width, height) # Наружные рамки
                item = QtWidgets.QGraphicsEllipseItem(rect)
                item.setPos(*position)
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Изображение
            elif item_type == "ImageItem":
                # Декодируем pixmap из Base64
                pixmap_data = item_data.get("pixmap")
                if pixmap_data:
                    pixmap = QtGui.QPixmap()
                    pixmap.loadFromData(QtCore.QByteArray.fromBase64(pixmap_data.encode("utf-8")))

                    # Получаем позицию из данных
                    position = item_data.get("position", {"x": 0, "y": 0})
                    x = position.get("x", 0)
                    y = position.get("y", 0)

                    # Создаём объект ImageItem
                    item = ImageItem(pixmap, x, y)

                    # Устанавливаем прозрачность, если она сохранена
                    opacity = item_data.get("opacity", 1.0)
                    item.setOpacity(opacity)

                    # Добавляем элемент на сцену
                    self.scene_.addItem(item)
                    self.objectS_.append(item)

            # Текстовое поле
            elif item_type == "Text_Edit":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                text = item_data.get("text", "")
                item = Text_Edit(x, y, width, height, text)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)

            # Синхронизатор
            elif item_type == "Splitter_Merge":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                rot = item_data.get("rotation") # Получаем положение
                color = item_data.get("color", "#000000") # Получаем цвет

                # Преобразование цвета
                if isinstance(color, str):
                    if color.startswith("#"):  # Если это HEX-строка
                        color = QtGui.QColor(color)
                    else:  # Если это предопределённый цвет
                        color = getattr(QtCore.Qt, color, QtCore.Qt.transparent)
                else:
                    color = QtGui.QColor()  # Цвет по умолчанию

                item = Splitter_Merge(x, y, width, height, rot, color=color)
                item.update_size_and_orientation(width, height, rot)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)

        # Вытаскиваем стрелки
        for arrow_data in data.get("arrows", []):
            # Идентификаторы
            start_node_id = arrow_data["start_node_id"]
            end_node_id = arrow_data["end_node_id"]

            # Получаем цвет, используем тёмно-красный (#8B0000) по умолчанию
            color_hex = arrow_data.get("color", "#8B0000")
            color = QColor(color_hex)  # Преобразуем HEX-строку в объект QColor

            width_of_pen = arrow_data.get("width") # Получаем толщину линии

            right_arrow = arrow_data.get("right_arrow") # Получаем правый наконечник
            left_arrow = arrow_data.get("left_arrow") # Получаем левый наконечник

            show_points = arrow_data.get("show_points") # Получаем флаг, показаны ли точки изгиба
            # Вытаскиваем по полученным идентификаторам из памяти
            start_node = self.get_element_by_id(start_node_id)
            end_node = self.get_element_by_id(end_node_id)
            #Рисуем стрелки
            if start_node and end_node:
                node1, node2 = start_node, end_node # Инициализируем узлы
                
                intermediate_points = [
                    QPointF(x, y) for x, y in arrow_data.get("dots", []) # Получаем точки изгиба
                ]

                arrow = Arrow(node1, node2, intermediate_points=intermediate_points) # Создаём объект стрелки вместе с точками изгиба

                # Устанавливаем тип линии
                line_type = arrow_data.get("line_type", "solid")  # Используем "solid" по умолчанию, если данных нет
                arrow.right_arrow_enabled = right_arrow # Правый наконечник
                arrow.left_arrow_enabled = left_arrow # Левый наконечник
                arrow.show_points = show_points # Видимость точек
                arrow.change_line_type(line_type)  # Применяем тип линии
                arrow.change_color(color)         # Устанавливаем цвет
                arrow.change_width(width_of_pen)
                arrow.setZValue(-1)
                self.scene_.addItem(arrow)  # Добавляем стрелку на сцену
                # Привязываем стрелку к обоим узлам
                node1.add_arrow(arrow)
                node2.add_arrow(arrow)
                # Обновляем стрелку сразу после добавления
                arrow.update_arrow()  # Обновляем стрелку вручную, если нужно
                self.scene_.update()

        # Добавляем элемент на сцену
        self.scene_.addItem(item)
        try:
            elements[position] = item
        except TypeError:
            pass  # Игнорировать ошибку и продолжить выполнение

    # Обработка кнопки "Создать"
    def create_new(self):
        self.reset_inaction()
        if len(self.objectS_) != 0:
            self.msg.setWindowTitle("Создание новой диаграммы")
            self.msg.setText("Вы уверены, что хотите создать новую диаграмму? Изменения не будут сохранены.")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            self.msg.setDefaultButton(QtWidgets.QMessageBox.No)

            reply = self.msg.exec_()

            if reply == QtWidgets.QMessageBox.Yes:
                self.objectS_.clear()
                self.scene_.clear()
                self.user_.add_action("Создана диаграмма UML", self.get_current_Realtime())
                self.reset_inaction()
            else:
                return
        else:
            self.objectS_.clear()
            self.scene_.clear()

    # Вставка изображения
    def insert_image(self):
        self.reset_inaction()
        # Открываем диалог для выбора изображения
        options = QtWidgets.QFileDialog.Options()
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Изображения (*.png *.jpg *.bmp);;Все файлы (*)", options=options
        )
        if not filepath:
            return  # Пользователь отменил выбор

        # Загружаем изображение
        pixmap = QtGui.QPixmap(filepath)
        if pixmap.isNull():
            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText(f"Не удалось загрузить изображение.")
            self.msg.exec_()
            return

        # Проверяем размер изображения
        if pixmap.width() > 200 or pixmap.height() > 200:
            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setWindowTitle("Ошибка")
            self.msg.setText(f"Размер изображения превышает допустимый предел (200x200). Текущее: {pixmap.width()}x{pixmap.height()}.")
            self.msg.exec_()
            return

        # Создаём объект изображения
        x, y = 200, 200  # Пример координат центра
        image_item = ImageItem(pixmap, x, y)
        self.scene_.addItem(image_item)  # Добавляем изображение на сцену

        # Добавляем объект в список объектов сцены
        self.objectS_.append(image_item)

        # Логика обновления интерфейса и отправки событий
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))
        self.populate_object_list()

        # Лог действий
        self.user_.add_action(f"Добавлен элемент '{image_item.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(
            self.user_.nickname,
            self.user_.user_id,
            self.user_.start_work,
            self.user_.end_work,
            next(reversed(self.user_.action_history)),
            next(reversed(self.user_.action_history.values())),
            self.user_.action_history
        )
    #Отображение окна статистики
    def show_static_widget(self):
        self.reset_inaction()
        # Создаем виджет статистики
        self.static_widget = QtWidgets.QWidget()  
        self.static_ui = Ui_StaticWidget()

        self.static_ui.setupUi(self.static_widget)  

        self.user_actions.connect(self.static_ui.uptade_static)

        self.static_ui.uptade_static(
            self.user_.nickname,
            self.user_.user_id,
            self.user_.start_work,
            self.user_.end_work,
            next(reversed(self.user_.action_history)),
            next(reversed(self.user_.action_history.values())),
            self.user_.action_history
        )

        # Подключаем другие сигналы
        self.time_updated.connect(self.static_ui.update_timeworkSW)
        self.update_last_timeSW.connect(self.static_ui.update_last_timeSW)
        self.count_objectS.connect(self.static_ui.get_count_objectS)

        # self.static_ui.accept_today(self.today, self.time_now, self.last_time)
        self.static_ui.accept_today(self.today, self.time_now, self.last_time)

        # Обновляем интерфейс через сигналы
        self.update_last_timeSW.emit(self.today, self.last_time, self.time_now)  
        self.count_objectS.emit(len(self.objectS_))

        # Устанавливаем заголовок и показываем окно
        self.static_widget.setWindowTitle("Статистика")  
        self.static_widget.show()  # Отображаем новый виджет


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "UML editor"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.menu_insert.setTitle(_translate("MainWindow", "Вставка"))
        self.menu_2.setTitle(_translate("MainWindow", "Статистика"))

        self.menu_3.setTitle(_translate("MainWindow", "Тест таймера"))

        self.menu_show_panel.setTitle(_translate("MainWindow", "Окна"))
        self.menu_help.setTitle(_translate("MainWindow", "Помощь"))
        self.action_edit_panel.setText(_translate("MainWindow", "Панель редактирования"))
        self.action_object_panel.setText(_translate("MainWindow", "Список объектов"))
        self.action_Toolbar.setText(_translate("MainWindow", "Тулбар"))

        

        self.action.setText(_translate("MainWindow", "Открыть"))
        self.action_2.setText(_translate("MainWindow", "Сохранить"))
        self.action_3.setText(_translate("MainWindow", "Сохранить как"))
        # self.action_PNG.setText(_translate("MainWindow", "Экспорт в PNG"))
        self.action_4.setText(_translate("MainWindow", "Создать"))
        self.action_settings.setText(_translate("MainWindow", "Настройки"))
        self.action_exit.setText(_translate("MainWindow", "Выход"))

        self.action_add_image.setText(_translate("MainWindow", "Изображение"))
        self.action_Statystics.setText(_translate("MainWindow", "Запустить статистику"))

        self.action_time_start.setText(_translate("MainWindow", "Запустить таймер"))
        self.action_time_stop.setText(_translate("MainWindow", "Остановить таймер"))
        self.action_time_reset.setText(_translate("MainWindow", "Сбросить таймер"))


    def setDesigh(self, MainWindow):

        MainWindow.setWindowIcon(QIcon("imgs/main_icon.png"))
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("imgs/main_icon.png"))
        self.tray_icon.setVisible(True)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.setToolTip("UML editor")

#         self.msg.setStyleSheet("""
                
# """)

        MainWindow.setStyleSheet("""
        QMenuBar {
            background-color: rgb(100, 100, 100); /* Тёмный фон */
            border: none; /* Без рамки */
        }

        QMenuBar::item {
            background-color: transparent; /* Прозрачный фон для пунктов меню */
            color: white; /* Белый цвет текста */
            padding: 8px 16px;
        }

        QMenuBar::item:selected {
            background-color: #4b4b4b; /* Цвет фона при наведении */
            color: #d3d3d3; /* Светлый цвет текста при наведении */
        }

        QMenu {
            background-color: #2f2f2f; /* Тёмный фон меню */
            border: 1px solid #555555; /* Тонкая рамка */
            border-radius: 5px; /* Закругленные углы */
        }

        QMenu::item {
            background-color: transparent; /* Прозрачный фон для пунктов меню */
            color: white; /* Белый цвет текста */
            padding: 8px 16px;
        }

        QMenu::item:selected {
            background-color: #4b4b4b; /* Цвет фона при выделении */
            color: #d3d3d3; /* Светлый цвет текста при выделении */
        }

        QMenu::item:pressed {
            background-color: #636363; /* Цвет фона при нажатии */
            color: white; /* Белый цвет текста при нажатии */
        }

        QMenu::indicator {
            border: none; /* Убираем стандартный индикатор */
        }

        QMenu::indicator:checked {
            background-color: #4CAF50; /* Цвет для отмеченных пунктов */
        }

        """)

        self.object_list_dock.setStyleSheet("""
        QDockWidget {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 8px;
        }

        QDockWidget::title {
            background-color: rgb(150, 150, 150);
            color: white;
            padding-left: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QDockWidget::close-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::close-button:hover {
            background-color: white;
            border-radius: 8px;  
        }                                      

        QDockWidget::float-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::float-button:hover {
            background-color: white;
            border-radius: 8px; 
        }
        """)

        self.dock_widget.setStyleSheet("""
        QDockWidget {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 8px;
        }

        QDockWidget::title {
            background-color: rgb(150, 150, 150);
            color: white;
            padding-left: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QDockWidget::close-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::close-button:hover {
            background-color: white;
            border-radius: 8px;  
        }                                      

        QDockWidget::float-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::float-button:hover {
            background-color: white;
            border-radius: 8px; 
        }

        QDockWidget QWidget {
            font-family: 'Arial';
            font-size: 14px;
            padding: 10px;
        }

        """)
        self.dock_widget.update() 
        self.ToolBarBox.setStyleSheet("""
            QFrame {
        background-color: rgb(240, 240, 240);
        border: 2px solid rgb(175, 175, 175);
        }

        QFrame QWidget {
            font-family: 'Arial';
            font-size: 14px;
            padding: 10px;
        }

        QPushButton {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(150, 150, 150);
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: rgb(220, 220, 220); 
            border: 1px solid rgb(100, 100, 100); 
        }

        QPushButton:pressed {
            background-color: rgb(200, 200, 200); 
        }
    """)
        self.object_list_widget.setStyleSheet("""
        QListWidget {
            border: none;
            background: rgb(250, 250, 250);
            border: 2px solid rgb(175, 175, 175);
            padding: 10px;
            font-weight: 500;
        }

        QListWidget::item {
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 16px;
            font-family: 'Arial';
            color: rgb(60, 60, 60);
            background-color: transparent; 
        }

        QListWidget::item:hover {
            background-color: rgb(240, 240, 240);
        }

        QListWidget::item:selected {
            background-color: rgb(169, 169, 169);
            color: white; 
            font-weight: bold;  
        }

        QListWidget::item:pressed {
            background-color: rgb(180, 230, 255);
        }

        QListWidget::indicator {
            border: none; 
        }

        QListWidget::indicator:checked {
            background-color: rgb(50, 150, 250);
            border-radius: 5px;
        }
        """)
        self.object_list_widget.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: none;
                width: 12px;
                margin: 5px 0 5px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgb(200, 200, 200);
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgb(180, 180, 180);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
        """)
        self.object_list_widget.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                border: none;
                background: none;
                height: 12px;
                margin: 0px 5px 0px 5px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgb(200, 200, 200);
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgb(180, 180, 180);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
        """)
        self.graphicsView.setObjectName("MyGraphicsView")
        self.graphicsView.setStyleSheet("""
            #MyGraphicsView {
                background-color: rgb(250, 250, 250);
                border: 2px solid rgb(200, 200, 200);
                border-radius: 10px;
            }
            #MyGraphicsView:hover {
                border-color: rgb(150, 150, 150);
            }
            
        """)

        self.graphicsView.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: none;
                width: 12px;
                margin: 5px 0 5px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgb(200, 200, 200);
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgb(180, 180, 180);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
        """)

        self.graphicsView.horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                border: none;
                background: none;
                height: 12px;
                margin: 0px 5px 0px 5px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgb(200, 200, 200);
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgb(180, 180, 180);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
        """)

        self.editing_dock.setStyleSheet("""QDockWidget {
            background-color: rgb(240, 240, 240);
            border: 1px solid rgb(200, 200, 200);
            border-radius: 8px;
        }

        QDockWidget::title {
            background-color: rgb(150, 150, 150);
            color: white;
            padding-left: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QDockWidget::close-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::close-button:hover {
            background-color: white;
            border-radius: 8px;  
        }                                      

        QDockWidget::float-button {
            width: 16px;
            height: 16px;
        }
                                            
        QDockWidget::float-button:hover {
            background-color: white;
            border-radius: 8px; 
        }""")

        QtWidgets.QToolTip.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

        # Устанавливаем стиль для подсказок через global stylesheet
        self.msg.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        app.setStyleSheet("""
            QToolTip {
                background-color: #f7f7f7;
                color: #333333;
                border: 2px solid #999999;
                padding: 5px;
                font-size: 16px;
                font-weight: 500;
            }
            QMessageBox {
                    background-color: #f5f5f5;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    font-size: 20px;
                    outline: none;
                    text-align: justify;
                }
                QMessageBox QLabel {
                    color: #333333;
                    padding: 5px;
                }
                QMessageBox QPushButton {
                    background-color: rgb(240, 240, 240);
                    border: 1px solid rgb(150, 150, 150);
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #2f2f2f;
                }
                QMessageBox QPushButton:hover {
                    background-color: rgb(220, 220, 220);
                    border: 1px solid rgb(100, 100, 100);
                }
                QMessageBox QPushButton:pressed {
                    background-color: rgb(200, 200, 200);
                }
                QMessageBox QFrame {
                    background-color: transparent;
                }
                QMessageBox QIcon {
                    margin-right: 10px;
                }
        """)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Это сработает при клике по иконке
            # Создаем контекстное меню для иконки
            tray_menu = QMenu()

            static = QAction(f"Просмотр статистики")
            quit_action = QAction("Выход")

            tray_menu.addAction(static)
            tray_menu.addAction(quit_action)
            static.triggered.connect(self.show_static_widget)
            quit_action.triggered.connect(self.quit_app)

            tray_menu.hovered.connect(self.on_menu_hovered)

            # Подсказки для действий. В данном случае показывает часть информации из статистики пользователя
            static.setData(f"""
                Пользователь - {self.user_.nickname}\n
                Начало работы - {self.today} {self.time_now}
""") # А именно - имя пользователя и когда он начал работу

            # Показываем контекстное меню в месте клика
            tray_menu.exec_(QCursor.pos())

    def on_menu_hovered(self, action):
        # Отображаем подсказку для текущего действия
        tooltip_text = action.data()  # Получаем текст подсказки из данных
        if tooltip_text:
            QToolTip.showText(QCursor.pos(), tooltip_text)

    # Выход из приложения через иконку в системном треи
    def quit_app(self):
        if len(self.objectS_) > 0: # Перед выходом проверяем наличее объектов на сцене
            # Если они есть предупреждаем об этом пользователя
            self.msg.setWindowTitle("Выход")
            self.msg.setText("Вы уверены, что хотите выйти? Изменения не будут сохранены.")
            self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            self.msg.setDefaultButton(QtWidgets.QMessageBox.No)

            # Отображение окна и получение ответа
            reply = self.msg.exec_()

            if reply == QtWidgets.QMessageBox.Yes: # Если пользователь всё равно хочет закрыть приложения
                QtWidgets.QApplication.quit()
        else: # Если сцена пуста, то приложение закроется без предупреждений
            QtWidgets.QApplication.quit()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Открытие окна входа
    login_window = LoginWindow()
    main_window = Ui_MainWindow()

    
    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        global_username = login_window.username_input.text()
        
        # Создаем и показываем основное окно
        main_window = QtWidgets.QMainWindow()  # Создаем объект для основного окна
        ui = Ui_MainWindow()  # Сюда можно вставить UI для основного окна
        ui.setupUi(main_window)  # Настроим интерфейс с UI
        main_window.show()

        sys.exit(app.exec_())  # Запуск основного цикла приложения
    else:
        sys.exit(app.quit())  # Завершаем приложение, если вход не был успешным
