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
from PyQt5.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QKeySequence

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

class EditingPanel(QWidget):
    def __init__(self, editable_item, main_window):
        super().__init__()
        self.editable_item = editable_item
        self.main_window = main_window

        # Используем QGridLayout вместо QVBoxLayout
        layout = QGridLayout()

        if isinstance(self.editable_item, Arrow):
            self.label_color = QLabel("Цвет стрекли")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_arrow_color)
            self.update_color_button_arrow()

            self.line_type_label = QLabel("Тип линии:")
            self.line_type_combo = QComboBox(self)
            self.line_type_combo.addItem("Сплошная")
            self.line_type_combo.addItem("Пунктирная")
            self.line_type_combo.addItem("Точечная")
            self.line_type_combo.addItem("Чередующая")

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

            layout.addWidget(self.label_color, 0, 0, 1, 1)
            layout.addWidget(self.color_button, 0, 1, 1, 1)
            layout.addWidget(self.line_type_label, 1, 0)
            layout.addWidget(self.line_type_combo, 1, 1)
            layout.addWidget(self.thickness_label, 2, 0)
            layout.addWidget(self.thickness_spinbox, 2, 1)
            layout.addWidget(self.right_arrow_checkbox, 3, 0)
            layout.addWidget(self.left_arrow_checkbox, 3, 1)
            layout.addWidget(self.show_points_checkbox, 4, 0)

        elif isinstance(self.editable_item, Decision):
            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            
            layout.addWidget(self.label_color, 0, 0, 1, 1)
            layout.addWidget(self.color_button, 0, 1, 1, 1)
            self.update_button_color()

        
        elif isinstance(self.editable_item, (StartEvent, EndEvent)):
            self.radius_label = QLabel("Радиус:")
            self.radius_spinbox = QSpinBox(self)
            self.radius_spinbox.setValue(int(self.editable_item.radius)) 
            self.radius_spinbox.setRange(5, 1000)
            self.radius_spinbox.valueChanged.connect(self.update_radius)
            
            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            layout.addWidget(self.label_color, 0, 0, 1, 1)
            layout.addWidget(self.color_button, 0, 1, 1, 1)
            layout.addWidget(self.radius_label, 1, 0, 1, 1)
            layout.addWidget(self.radius_spinbox, 1, 1, 1, 1)


        elif isinstance(self.editable_item, (ActiveState, SignalSending, SignalReceipt)):
            self.width_label = QLabel("Ширина:")
            self.width_spinbox = QSpinBox(self)
            self.width_spinbox.setValue(int(self.editable_item.boundingRect().width()))
            self.width_spinbox.valueChanged.connect(self.update_width)
            self.width_spinbox.setRange(10, 1000)

            self.height_label = QLabel("Высота:")
            self.height_spinbox = QSpinBox(self)
            self.height_spinbox.setValue(int(self.editable_item.boundingRect().height()))
            self.height_spinbox.valueChanged.connect(self.update_height)
            self.height_spinbox.setRange(10, 1000)

            self.text_label = QLabel("Текст:")
            self.text_input = QLineEdit(self)
            self.text_input.setText(self.editable_item.text_item.toPlainText())
            self.text_input.setMaxLength(15)
            self.text_input.textChanged.connect(self.update_text)

            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            layout.addWidget(self.label_color, 0, 0 , 1, 1)
            layout.addWidget(self.color_button, 0, 1, 1, 1)
            layout.addWidget(self.width_label, 1, 0, 1, 1)
            layout.addWidget(self.width_spinbox, 1, 1, 1, 1)
            layout.addWidget(self.height_label, 2, 0, 1, 1)
            layout.addWidget(self.height_spinbox, 2, 1, 1, 1)
            layout.addWidget(self.text_label, 3, 0, 1, 1)
            layout.addWidget(self.text_input, 3, 1, 1, 1)

        elif isinstance(self.editable_item, (Splitter_Merge)):

            self.label_color = QLabel("Цвет заливки")
            self.color_button = QPushButton("")
            self.color_button.clicked.connect(self.change_color)
            self.update_button_color()

            self.width_label = QLabel("Длинна:")
            self.width_spinbox = QSpinBox(self)
            self.width_spinbox.setValue(int(self.editable_item.boundingRect().width()))
            self.width_spinbox.valueChanged.connect(self.update_width)
            self.width_spinbox.setRange(10, 1000)

            self.height_label = QLabel("Толщина:")
            self.height_spinbox = QSpinBox(self)
            self.height_spinbox.setValue(int(self.editable_item.boundingRect().height()))
            self.height_spinbox.valueChanged.connect(self.update_height)
            self.height_spinbox.setRange(10, 1000)

            
            self.orint_label = QLabel("Положение:")
            self.orint_combo = QComboBox(self)
            self.orint_combo.addItem("Вериткально")
            self.orint_combo.addItem("Горизонатльно")
            self.orint_combo.currentTextChanged.connect(self.update_orientation)

            if self.editable_item.rotation() == 0: # Если горизонатльно, значит в combobox установится значение горизонатльно
                self.orint_combo.setCurrentIndex(1)
            else: # иначе вертикально
                self.orint_combo.setCurrentIndex(0)  

            layout.addWidget(self.label_color, 0, 0, 1, 1)
            layout.addWidget(self.color_button, 0, 1, 1, 1)
            layout.addWidget(self.width_label, 1, 0, 1, 1)
            layout.addWidget(self.width_spinbox, 1, 1, 1, 1)
            layout.addWidget(self.height_label, 2, 0, 1, 1)
            layout.addWidget(self.height_spinbox, 2, 1, 1, 1)
            layout.addWidget(self.orint_label, 3, 0)
            layout.addWidget(self.orint_combo, 3, 1)
        
        elif isinstance(self.editable_item, (ImageItem)):

            self.opacity_label = QLabel("Прозрачность:")
            self.opacity_slider = QSlider(Qt.Horizontal)
            self.opacity_slider.setRange(0, 100)
            self.opacity_slider.setValue(int(self.editable_item.opacity() * 100))
            self.opacity_slider.valueChanged.connect(self.update_opacity)

            layout.addWidget(self.opacity_label, 0, 0, 1, 1)
            layout.addWidget(self.opacity_slider, 0, 1, 1, 1)

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
            layout.addWidget(self.text_label, 0, 0, 1, 1)
            layout.addWidget(self.text_area, 1, 0, 1, 0)
            layout.addWidget(self.count_sim_label1, 2, 0, 1, 1)
            layout.addWidget(self.count_sim_input2, 2, 1, 1, 1)


        else:
            self.message_label = QLabel("В разработке")
            layout.addWidget(self.message_label, 0, 0, 1, 2)

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
        self.copy_item.clicked.connect(self.duplicate_current_item)


        layout.addWidget(self.x_label, 6, 0)
        layout.addWidget(self.x_spinbox, 6, 1)
        layout.addWidget(self.y_label, 7, 0)
        layout.addWidget(self.y_spinbox, 7, 1)
        layout.addWidget(self.delete_item, 8, 0)
        layout.addWidget(self.copy_item, 8, 1)


        self.setLayout(layout)

        self.setMinimumWidth(200)
        self.setMaximumWidth(400)

    def delete_current_item(self):
        if self.editable_item:
            # self.editable_item.setSelected(True)  # Выделяем текущий объект
            self.main_window.delete_specific_item(self.editable_item)    

    def update_position(self):
        if self.editable_item:
            # Получаем глобальные координаты объекта на сцене
            scene_pos = self.editable_item.mapToScene(self.editable_item.pos())  # Преобразуем в глобальные координаты
            new_x = scene_pos.x()  # Глобальная X-координата
            new_y = scene_pos.y()  # Глобальная Y-координата

            self.x_spinbox.setValue(new_x)
            self.y_spinbox.setValue(new_y)

    def update_coordinates(self, x, y):
        if self.is_position_updating:
            return  # Прерываем, если уже идет обновление позиции
        self.is_position_updating = True  # Устанавливаем флаг
        self.x_spinbox.setValue(x)
        self.y_spinbox.setValue(-y)  # Инвертируем Y перед обновлением SpinBox
        self.is_position_updating = False

    #Если пользователь хочет поменять позицию объекта через панель редактирования
    def update_position_from_spinbox(self):
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
        color = QColorDialog.getColor()
        if color.isValid():
            self.editable_item.change_color(color)
            self.update_color_button_arrow()

    def update_color_button_arrow(self):
        current_color = self.editable_item.pen.color()  # Получаем цвет из pen у стрелки
        self.color_button.setStyleSheet(f"""
                background-color: {current_color.name()};
                border: 2px solid rgb(173, 173, 173);
""")

    def update_line_type(self):
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
        self.editable_item.right_arrow_enabled = bool(state)
        self.editable_item.update_arrow()

    def toggle_left_arrow(self, state):
        self.editable_item.left_arrow_enabled = bool(state)
        self.editable_item.update_arrow()

    def toggle_points_visibility(self, state):
        self.editable_item.show_points = bool(state)
        self.editable_item.update()

    def update_arrow_thickness(self, thickness):
        self.editable_item.change_width(thickness)

    def update_text(self):
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
        if isinstance(self.editable_item, Splitter_Merge):
            orientation = self.orint_combo.currentText()  # Получаем выбранный текст
            if orientation == "Вериткально":
                width, height = self.editable_item.height, self.editable_item.width
                temp_s = width #Перед поротом меняем ширину и высоту местами
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
        new_width = self.width_spinbox.value()
        if hasattr(self.editable_item, 'setRect'):
            rect = self.editable_item.boundingRect()
            self.editable_item.setRect(rect.x(), rect.y(), new_width, rect.height())
        elif hasattr(self.editable_item, 'update_size'):
            rect = self.editable_item.boundingRect()
            self.editable_item.update_size(new_width, rect.height())
        else:
            print(f"Cannot update width for {type(self.editable_item).__name__}")

    def update_height(self):
        new_height = self.height_spinbox.value()
        if hasattr(self.editable_item, 'setRect'):
            rect = self.editable_item.boundingRect()
            self.editable_item.setRect(rect.x(), rect.y(), rect.width(), new_height)
        elif hasattr(self.editable_item, 'update_size'):
            rect = self.editable_item.boundingRect()
            self.editable_item.update_size(rect.width(), new_height)
        else:
            print(f"Cannot update height for {type(self.editable_item).__name__}")

    def update_radius(self):
        if isinstance(self.editable_item, (StartEvent, EndEvent)):
            new_radius = self.radius_spinbox.value()
            self.editable_item.setRadius(new_radius)  # Обновляем радиус

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
        color = QColorDialog.getColor()
        if color.isValid():
            self.editable_item.setBrush(QBrush(color))
            self.update_button_color()

    def update_button_color(self):
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
        opacity = self.opacity_slider.value() / 100
        self.editable_item.setOpacity(opacity)


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
            return SignalSending(0, 25, 80, 50)

    def create_sending_receipt_in_tulbar(self):
        if self.element_type == "SignalReceipt":
            return SignalReceipt(0, 25, 100, 50)

    def create_splitter_merge_horizontal_in_tulbar(self):
        if self.element_type == "Splitter_Merge_Horizontal":
            return Splitter_Merge(0, 10, 100, 30)

    def create_splitter_merge_vertical_in_tulbar(self):
        if self.element_type == "Splitter_Merge_Vertical":
            return Splitter_Merge(0, 0, 60, 30)

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


    def drawBackground(self, painter, rect):
        # Включаем сглаживание
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)  # Для сглаживания изображения

        super().drawBackground(painter, rect)

    def mousePressEvent(self, event):

        # self.clicks.append(event.scenePos())

        selected_item = self.itemAt(event.scenePos(), QtGui.QTransform())  # Находим элемент под курсором
  
        if selected_item:
            self.reset_time.stop_inaction()
            self.is_dragging = True
            self.reset_time.show_editing_panel(selected_item)
            # Устанавливаем текст в label_x_y с названием класса элемента
            element_name = type(selected_item).__name__
            mouse_pos = event.scenePos()
            self.label.setText(f"Выбрано: {element_name} ({mouse_pos.x():.1f}, {-mouse_pos.y():.1f})")

            # self.reset_time.on_object_selected(selected_item)

            item_rect = selected_item.sceneBoundingRect()
            item_center = item_rect.center()  # Центр объекта
            print(f"Выбран объект {element_name} с центром координат: ({item_center.x():.1f}, {-item_center.y():.1f})")
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
                    self.selection_rect.setPen(QtGui.QPen(QtGui.QColor(0, 0, 255, 150)))  # линия для выделения
                    self.selection_rect.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255, 50)))  # Прозрачный цвет внутри
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
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
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
            item = SignalSending(position.x(), position.y(), 160, 60)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "SignalReceipt":
            item = SignalReceipt(position.x(), position.y(), 180, 60)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "Splitter_Merge_Horizontal":
            item = Splitter_Merge(position.x(), position.y(), 120, 40)
            item.setRotation(0)
            print(f"Created {item.__class__.__name__} with unique_id: {item.unique_id}")

        elif element_type == "Splitter_Merge_Vertical":
            item = Splitter_Merge(position.x(), position.y(), 120, 40)
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
            if len(self.objectS) > 10:
                self.reset_time.message_overcrowed_objectS()
        else:
            # Если item (например фрагмент Text_Edit)не распознан, отклоняем событие
            event.ignore()

    def dragMoveEvent(self, event):
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
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout()
        
        instruction_text = QTextEdit()
        instruction_text.setReadOnly(True)
        instruction_text.setText(self.load_instruction())
        
        layout.addWidget(instruction_text)
        self.setLayout(layout)

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


# Окно входа
class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход или регистрация")
        
        # Получаем размеры экрана для центрирования окна
        screen_geometry = QtWidgets.QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()

        # Устанавливаем начальный размер окна
        self.setFixedSize(300, 400)

        # Центрируем окно, учитывая его размеры
        window_size = self.size()
        self.move(screen_center.x() - window_size.width() // 2, screen_center.y() - window_size.height() // 2)


        self.user_data_folder = "user_data"
        os.makedirs(self.user_data_folder, exist_ok=True)

        layout = QtWidgets.QVBoxLayout(self)

        # Добавление изображения
        self.logo_label = QtWidgets.QLabel(self)
        self.logo_pixmap = QtGui.QPixmap("imgs/ctuaslogo.jpg")  # Убедись, что путь корректный
        self.logo_pixmap = self.logo_pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio)
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
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

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
                global global_start_time # Получаем время начала работы
                global_start_time = user_data.get("start_time")

                QtWidgets.QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
                self.accept()  # Закрыть окно с результатом успешного входа
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")

    # Регистрация
    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if len(username) > 3 and len(password) > 3:
            user_file = os.path.join(self.user_data_folder, f"{username}.json")

            if os.path.exists(user_file):
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")
                return
            
            hashed_password = self.hash_password(password)
            user_data = {
                "username": username,
                "password": hashed_password,
                "start_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "end_time": None
            }

            global global_start_time # Получаем время начала работы
            global_start_time = user_data.get("start_time")

            with open(user_file, "w") as f:
                json.dump(user_data, f)

            QtWidgets.QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован!")
            self.accept()  # Закрыть окно с результатом успешной регистрации
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Логин и пароль должны быть длиннее 3 символов!")



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
        self.ToolBarBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.ToolBarBox.setFont(font)
        self.ToolBarBox.setStyleSheet("background-color: rgb(255, 255, 255);")
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
        pixmap = QtGui.QPixmap("imgs/ctuaslogo.jpg")
        if not pixmap.isNull():
            self.logoLabel.setPixmap(pixmap.scaled(
                150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.logoLabel.setText("Логотип\nне найден")
        
        self.gridLayout_6.addWidget(self.logoLabel, 0, 1, 1, 1)  # Логотип справа


        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        #self.gridLayout_6.addWidget(self.frame, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.label_x_y = QtWidgets.QLabel(MainWindow)
        self.label_x_y.setObjectName("label_x_y")
        self.label_x_y.setAlignment(QtCore.Qt.AlignRight)
        self.label_x_y.setStyleSheet("""
QLabel {
            color: gray;                         }""")
        self.label_x_y.setText("(0, 0)")
        self.gridLayout_2.addWidget(self.label_x_y, 2, 1, 1, 1)


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
        self.action_PNG = QtWidgets.QAction(MainWindow)
        self.action_PNG.setObjectName("action_PNG")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
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
        self.menu.addAction(self.action_PNG)
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
        #self.timer_2.start(1000)  # Запускаем таймер с интервалом в 1 секунду

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


        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)

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

        self.connect_objectS = QShortcut(QKeySequence("Ctrl+S"), self.graphicsView)
        self.connect_objectS.activated.connect(self.save_to_file)

        
        self.connect_objectS = QShortcut(QKeySequence("Ctrl+N"), self.graphicsView)
        self.connect_objectS.activated.connect(self.create_new)

        
        self.connect_objectS = QShortcut(QKeySequence("Ctrl+M"), self.graphicsView)
        self.connect_objectS.activated.connect(self.show_static_widget)

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
        # self.connect_objectS = QShortcut(QKeySequence("T"), self.graphicsView)
        # self.connect_objectS.activated.connect(self.disconnect_nodes)


        self.user_ = User(self.username, 0, self.start_time, self.get_time_for_user(self.last_time))
        self.user_.add_action("Создана диаграмма UML", self.start_time)
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)


        self.scene_ = My_GraphicsScene(self, self.objectS_, self.user_, self.label_x_y)
        self.graphicsView.setScene(self.scene_)  # Устанавливаем сцену в QGraphicsView

        self.editing_dock = QtWidgets.QDockWidget("Панель редактирования", MainWindow)
        self.editing_dock.setObjectName("editing_dock")
        editing_widget = QtWidgets.QWidget()
        self.editing_dock.setWidget(editing_widget)
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
        MainWindow.tabifyDockWidget(self.object_list_dock, self.dock_widget) #Размещаем dockwidget'ы одновременно, чтобы сразу через них можно было переключаться
        self.object_list_dock.setMinimumWidth(100)
        self.object_list_dock.setMaximumWidth(150)
        self.object_list_widget.itemClicked.connect(self.on_object_selected)
        self.populate_object_list()


    def show_toolbar(self):
        self.dock_widget.setVisible(True)
    def show_edit_panel(self):
        self.editing_dock.setVisible(True)
    def show_object_panel(self):
        self.object_list_dock.setVisible(True)

    def populate_object_list(self):
        self.object_list_widget.clear()
        for index, item in enumerate(self.objectS_):
            list_item_text = f"#{item.unique_id}: {type(item).__name__}"
            list_item = QtWidgets.QListWidgetItem(list_item_text)
            self.object_list_widget.addItem(list_item)

    def show_help(self):
        if not self.help_window:
            self.help_window = HelpWindow()
        self.help_window.show()

    def on_object_selected(self, item):
        # Получаем объект, привязанный к элементу списка
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

            # Передаем координаты центра в панель редактирования
        self.scene_.coordinates_updated.emit(global_center.x(), global_center.y())


    def update_coordinates_in_panel(self, x, y):
       # обновление координат в панели редактирования
        if self.editing_panel:
            self.editing_panel.update_coordinates(x, y)


    # Быстрое сохранение в папку saves
    def save_to_file(self, filepath=None):
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
                start_node_id = item.node1.unique_id  # Получаем id начального узла
                end_node_id = item.node2.unique_id    # Получаем id конечного узла

                data["arrows"].append({
                    "start_node_id": start_node_id,
                    "end_node_id": end_node_id
                })

        try:
            # Сохраняем данные в файл
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print("Файл сохранён:", filepath)
            QtWidgets.QMessageBox.information(self, "Сохранение", f"Файл успешно сохранён в:\n{filepath}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    # Сохранение с пользовательским названием в конкретное место
    def save_as(self, filepath=None):
        if not filepath:  # Если путь не задан, запрашиваем его у пользователя
            options = QtWidgets.QFileDialog.Options()
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "CHEP Files (*.chep);;All Files (*)", options=options
            )
            if not filepath:
                return

        data = {"items": [], "arrows": []}
        elements = {}

        # Сохраняем элементы
        for item in self.scene_.items():
            if isinstance(item, QtWidgets.QGraphicsItem):
                item_data = self.serialize_item(item)
                data["items"].append(item_data)
                elements[item.unique_id] = item  # Сохраняем элементы по их уникальному идентификатору

                if isinstance(item, Arrow):  # Если элемент - стрелка
                    arrow_data = {
                        "start_node_id": item.node1.unique_id,  # Сохраняем идентификаторы узлов
                        "end_node_id": item.node2.unique_id,
                    }
                    data["arrows"].append(arrow_data)

        try:
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print("Файл сохранён:", filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    # Открытие файла
    def open_file(self):
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
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")

    # Сериализация элементов для их дальнейшего сохранения
    def serialize_item(self, item):
        print('Вызвано')
        base_data = {
            "type": type(item).__name__,      # Тип элемента
            "position": (item.x(), item.y()), # Позиция элемента
            "size": None,                    # Размер (например, для Decision)
            "radius": None,                  # Радиус (например, для StartEvent и EndEvent)
            "inner_radius_ratio": None,      # Соотношение радиусов (EndEvent)
            "width": None,                   # Ширина (например, для ActiveState)
            "height": None,                  # Высота (например, для ActiveState)
            "text": None,                    # Текст (например, для ActiveState)
            "start_node": None,              # Начальная точка (для Arrow)
            "end_node": None,                # Конечная точка (для Arrow)
            "color": None,                   # Цвет линии (для Arrow)
            "line_width": None,              # Толщина линии (для Arrow)
            "start_node": None,              # Начальная точка соединения (для Arrow)
            "end_node": None,                # Конечная точка соединения (для Arrow)
            "color": None,                   # Цвет линии (для Arrow)
            "line_width": None,              # Ширина линии
            "id": None                       # Идентификатор
        }

       
        # Заполняем структуру в зависимости от типа элемента
        if isinstance(item, Decision):  # Ромб
            base_data["size"] = item.size
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()/ 2
            y = p_center.y() / 2
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id
            # Проверяем, является ли цвет экземпляром QColor
            if isinstance(item.color, QtGui.QColor):
                base_data["color"] = item.color.name()  # Сохраняем как HEX
            else:
                # Для предопределённых цветов сохраняем их название
                base_data["color"] = str(item.color)  # Например, 'transparent'

        elif isinstance(item, StartEvent):  # Круг (начало)
            rect = item.rect()
            base_data["radius"] = rect.width() / 2
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y()
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id

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

        elif isinstance(item, ActiveState):  # Прямоугольник с закругленными углами
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()
            base_data["radius"] = rect.width() / 6
            base_data["text"] = item.text_item.toPlainText() if hasattr(item, "text_item") else None
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x() - 50
            y = p_center.y() - 30
            print(x, y)
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id

        elif isinstance(item, SignalSending):  # Пентагон (сигнал отправки)
            rect = item.boundingRect()
            base_data["width"] = item.width
            base_data["height"] = item.height
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x() - 15
            y = p_center.y() + 30
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id

        elif isinstance(item, SignalReceipt):  # Пентагон (сигнал получения)
            rect = item.boundingRect()
            base_data["width"] = item.width
            base_data["height"] = item.height
            position = item.sceneBoundingRect()
            p_center = position.center()
            x = p_center.x()
            y = p_center.y() + 30
            base_data["position"] = {"x": x, "y": y}
            base_data["id"] = item.unique_id

        

        elif isinstance(item, QtWidgets.QGraphicsEllipseItem):  # Простой круг
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()

        # Возвращаем структуру со всеми ключами
        return base_data

    # Закрытие приложения
    def close_application(self):
        self.close()

    # Обработка кнопки 'Выход'
    def closeEvent(self, event):
        if len(self.objectS_) > 0:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Выход",
                "Вы уверены, что хотите выйти? Изменения не будут сохранены.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                print('egre')
                QtWidgets.QApplication.quit()
            else:
                event.ignore()
        else:
            QtWidgets.QApplication.quit()
    
    def message_overcrowed_objectS(self):
        if len(self.objectS_) > 10:
            self.reset_inaction() #Сбрасыем второй таймер
            self.count_objectS.emit(len(self.objectS_) - 1)
            self.scene_.removeItem(self.objectS_[len(self.objectS_) - 1])
            del self.objectS_[len(self.objectS_) - 1]
            self.populate_object_list()
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Превышено максимальное значение элементов")
            msgBox.setWindowTitle("Предупреждение")
            msgBox.setStandardButtons(QMessageBox.Ok )
            # msgBox.buttonClicked.connect(msgButtonClick)
            self.user_.pop_action()
            self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

            returnValue = msgBox.exec()

    # def message_arrow(self):
    #     msgBox = QMessageBox()
    #     msgBox.setIcon(QMessageBox.Information)
    #     msgBox.setText("Стрелка уже существует между выбранными элементами")
    #     msgBox.setWindowTitle("Предупреждение")
    #     msgBox.setStandardButtons(QMessageBox.Ok )


    # def add_text_edit(self, x, y, width, height, text="Введите текст"):
    #     text_item = Text_Edit(x, y, width, height, text)
    #
    #     text_item.setFlags(
    #         QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)  # Позволяет перемещать и выделять
    #     self.scene_.addItem(text_item)  # Добавляем текстовое поле на сцену

    def add_text(self):
        text_item = Text_Edit(0, 0, 100, 30, "Текст")
        self.scene_.addItem(text_item)
        self.objectS_.append(text_item)
        self.populate_object_list()
        self.count_objectS.emit(len(self.objectS_))
        self.user_.add_action(f"Добавлен элемент '{text_item.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_diamond(self):
        # self.reset_inaction() #Сбрасыем второй таймер
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
        # self.reset_inaction() #Сбрасыем второй таймер
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
        # self.reset_inaction() #Сбрасыем второй таймер
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
        # self.reset_inaction() #Сбрасыем второй таймер
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
        # self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, size = 0, 0, 100  # Пример координат, размера и радиуса
        pentagon = SignalSending(x, y, 160, 60)
        self.scene_.addItem(pentagon)  # Добавляем закругленный прямоугольник на сцену
        self.objectS_.append(pentagon)
        self.populate_object_list()

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_pentagon_reverse(self):
        # self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, size = 0, 0, 100  # Пример координат, размера и радиуса
        pentagon = SignalReceipt(x, y, 180, 60)
        pentagon.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(pentagon)  # Добавляем закругленный прямоугольник на сцену
        self.objectS_.append(pentagon)
        self.populate_object_list()
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())), self.user_.action_history)

    def draw_splitter_merge_h(self):
        # self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y = 0, 0  # Пример координат, размера и радиуса
        stick = Splitter_Merge(x, y, 120, 40)
        stick.setRotation(0)
        self.scene_.addItem(stick) 
        self.objectS_.append(stick)
        self.populate_object_list()
        self.user_.add_action(f"Добавлена конструкция Spliter_Merge'", self.get_current_Realtime())
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

    def draw_splitter_merge_v(self):
        # self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y = 0, 0  # Пример координат, размера и радиуса
        stick = Splitter_Merge(x, y, 120, 40)
        stick.setRotation(90)
        self.scene_.addItem(stick) 
        self.objectS_.append(stick)
        self.populate_object_list()
        self.user_.add_action(f"Добавлена конструкция Spliter_Merge'", self.get_current_Realtime())
        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))



    def add_edge(self):
        # self.reset_inaction() #Сбрасыем второй таймер
        selected_nodes = [object_ for object_ in self.objectS_ if object_.isSelected()]
        # Обработка случая, когда пользователь хочет соединить более двух элементов
        if len(selected_nodes) > 2:
            warn = QMessageBox()
            warn.setIcon(QMessageBox.Warning)
            warn.setWindowTitle('Внимание')
            warn.setText('Нельзя соединить более двух элементов одновременно.')
            warn.setStandardButtons(QMessageBox.Ok)
            warn.exec_()
        # Обработка случая, когда пользователь хочет соединить менее двух элементов
        if len(selected_nodes) < 2:
            warn = QMessageBox()
            warn.setIcon(QMessageBox.Warning)
            warn.setWindowTitle('Внимание')
            warn.setText('Выберите два элемента для соединения.')
            warn.setStandardButtons(QMessageBox.Ok)
            warn.exec_()

        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes
            print(node1)

            # Проверяем, существует ли уже стрелка между node1 и node2
            for arrow in node1.arrows:
                if (arrow.node1 == node1 and arrow.node2 == node2) or (arrow.node1 == node2 and arrow.node2 == node1):
                    disconnect = QMessageBox.question(
                        None,
                        "Предупреждение",
                        "Стрелка уже существует между выбранными элементами. Вы хотите удалить её?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if disconnect == QMessageBox.Yes:
                        self.disconnect_nodes(node1, node2)
                    return

            # Создаем стрелку и привязываем её к выбранным узлам
            arrow = Arrow(node1, node2)
            arrow.setZValue(-1)
            self.scene_.addItem(arrow)  # Добавляем стрелку на сцену

            # Привязываем стрелку к обоим узлам
            node1.add_arrow(arrow)
            node2.add_arrow(arrow)

            # Обновляем стрелку сразу после добавления
            arrow.update_arrow()  # Обновляем стрелку вручную, если нужно
            self.scene_.update()  # Перерисовываем сцену
            self.user_.add_action(f"Соединены '{node1.__class__.__name__}' и '{node2.__class__.__name__}'", self.get_current_Realtime())
    
    def select_all_item(self):
        # self.reset_inaction()
        for item in self.scene_.items():
            # Проверяем может ли элемент выделяться
            if isinstance(item, QtWidgets.QGraphicsItem):
                item.setSelected(True)

    def disconnect_nodes(self, node1, node2):
        if hasattr(node1, 'arrows') and hasattr(node2, 'arrows'):
            for arrow in node1.arrows[:]:
                if (arrow.node1 == node2 or arrow.node2 == node2) and arrow in node2.arrows:
                    self.user_.add_action(f"Рассоединены '{node1.__class__.__name__}' и '{node2.__class__.__name__}'", self.get_current_Realtime())
                    arrow.remove_arrow()
        self.scene_.update()




                
    def delete_selected_item(self):
        # self.reset_inaction()  # Сбрасываем второй таймер
        selected_items = self.scene_.selectedItems()

        for item in selected_items:
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
                    del arrows_to_remove

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

                if (len(self.objectS_)> 10):
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



    # def count_objectS(self):
    #     return len(self.objectS_)



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
            # self.timer_2.stop()
            self.last_time = self.Start_Time.text()  # Сохраняем текущее значение времени перед остановкой

            self.today_uptadet = self.get_current_Date()
            self.time_now_uptadet = self.get_current_Realtime()


            self.running_inaction = False
            self.timer_inaction.stop()

            print("Таймер остален")

            self.time_updated.emit(self.today_uptadet, self.last_time, self.time_now_uptadet)

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText(f"Работа приостановлена в {self.get_current_Realtime()}. Программа ожидает отклика пользователя")
            msgBox.setWindowTitle("Предупреждение")
            msgBox.setStandardButtons(QMessageBox.Ok)
            returnValue = msgBox.exec()

            if returnValue == QMessageBox.Ok:
                self.reset_inaction()

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

        if self.Time_inaction.text() == "00:00:30":
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
        for item in self.objectS_:
            print(f"Checking item: {item}")
            print(f"Item type: {type(item)}")
            print(f"Item unique_id: {getattr(item, 'unique_id', None)}")
            if item.unique_id == id:
                print(f"Returning item with id:' {getattr(item, 'unique_id', None)}")
                return item
        return None
    
    # Получение данных из открытого файла
    def load_from_data(self, data):
        self.objectS_.clear()
        self.scene_.clear() 
        elements = {}  # Словарь для хранения элементов по их координатам
        for item_data in data["items"]:
            item_type = item_data["type"]
            position = item_data["position"]

            # Создание объектов в зависимости от типа
            if item_type == "Decision":
                size = item_data.get("size")  # Достаём "size" с умолчанием
                color = item_data.get("color", "#000000")
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

                item = Decision(x, y, size, color)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)
                # Устанавливаем точную позицию
                item.setPos(x, y)

            elif item_type == "StartEvent":
                radius = item_data.get("radius", 30)  # Достаём "radius" с умолчанием
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                item = StartEvent(x, y, radius)
                print('id now:', item.unique_id)
                item.unique_id = item_data.get("id")
                print('id after:', item.unique_id)
                self.scene_.addItem(item)
                self.objectS_.append(item)

            elif item_type == "EndEvent":
                radius = item_data.get("radius", 30)
                inner_radius_ratio = item_data.get("inner_radius_ratio", 0.5)
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                item = EndEvent(x, y, radius, inner_radius_ratio)
                item.unique_id = item_data.get("id")
                
                self.scene_.addItem(item)
                self.objectS_.append(item)

            elif item_type == "ActiveState":
                width = item_data.get("width", 100)
                height = item_data.get("height", 50)
                radius = item_data.get("radius", 10)
                text = item_data.get("text", "")
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                item = ActiveState(x, y, width, height, radius)
                item.unique_id = item_data.get("id")
                item.text_item.setPlainText(text)
                
                self.scene_.addItem(item)
                self.objectS_.append(item)

            elif item_type == "SignalSending":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                item = SignalSending(x, y, width, height)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)

            elif item_type == "SignalReceipt":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                position_data = item_data.get("position")
                x, y = position_data.get("x"), position_data.get("y")
                item = SignalReceipt(x, y, width, height)
                item.unique_id = item_data.get("id")
                self.scene_.addItem(item)
                self.objectS_.append(item)

            elif item_type == "QtWidgets.QGraphicsEllipseItem":
                width = item_data.get("width", 60)
                height = item_data.get("height", 60)
                rect = QRectF(-width / 2, -height / 2, width, height)
                item = QtWidgets.QGraphicsEllipseItem(rect)
                item.setPos(*position)
                self.scene_.addItem(item)
                self.objectS_.append(item)

        # Вытаскиваем стрелки
        for arrow_data in data.get("arrows", []):
            # Идентификаторы
            start_node_id = arrow_data["start_node_id"]
            end_node_id = arrow_data["end_node_id"]
            # Вытаскиваем по полученным идентификаторам из памяти
            start_node = self.get_element_by_id(start_node_id)
            end_node = self.get_element_by_id(end_node_id)
            #Рисуем стрелки
            if start_node and end_node:
                node1, node2 = start_node, end_node
                # Создаем стрелку и привязываем её к выбранным узлам
                arrow = Arrow(node1, node2)
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
        elements[position] = item

    # Обработка кнопки "Создать"
    def create_new(self):
        if len(self.objectS_) != 0:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Создание новой диаграммы",
                "Вы уверены, что хотите создать новую диаграмму? Изменения не будут сохранены.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                self.objectS_.clear()
                self.scene_.clear()
                self.user_.add_action("Создана диаграмма UML", self.get_current_Realtime())
            else:
                return
        else:
            self.objectS_.clear()
            self.scene_.clear()

    # Вставка изображения
    def insert_image(self):
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
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение.")
            return

        # Проверяем размер изображения
        if pixmap.width() > 200 or pixmap.height() > 200:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                f"Размер изображения превышает допустимый предел (200x200). Текущее: {pixmap.width()}x{pixmap.height()}."
            )
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
        self.ToolBarBox.setTitle(_translate("MainWindow", "Панель инструментов"))
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
        self.action_PNG.setText(_translate("MainWindow", "Экспорт в PNG"))
        self.action_4.setText(_translate("MainWindow", "Создать"))
        self.action_exit.setText(_translate("MainWindow", "Выход"))

        self.action_add_image.setText(_translate("MainWindow", "Изображение"))
        self.action_Statystics.setText(_translate("MainWindow", "Запустить статистику"))

        self.action_time_start.setText(_translate("MainWindow", "Запустить таймер"))
        self.action_time_stop.setText(_translate("MainWindow", "Остановить таймер"))
        self.action_time_reset.setText(_translate("MainWindow", "Сбросить таймер"))

        def set_username(self, username):
            self.username = username
            self.update_ui()  # Обновляем интерфейс


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
