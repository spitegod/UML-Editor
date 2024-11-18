import os
import sys
from math import *
from PyQt5 import QtCore, QtGui, QtWidgets
from Static import Ui_StaticWidget  # Импортируем класс Ui_StaticWidget
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QShortcut, QMessageBox
from PyQt5.QtCore import QTimer, QTime, QDateTime
from PyQt5.QtCore import pyqtSignal  # Импортируем pyqtSignal
from PyQt5.QtCore import Qt, QPointF, QLineF
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QKeySequence

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#Тест, чтобы проверить видимость изображения
png_ = "imgs/startstate.png" #Сюда вбиваете путь изображения, который хотите проверить
if not os.path.exists(png_):
    print(f"Файл не найден по указанному пути: {png_}")
else:
    print("Файл найден!")

#Класс с информацией об одном Пользователе
class User:
    def __init__(self, nickname: str, user_id: int, start_work: str, end_work: str) -> None:
        self.nickname = nickname
        self.user_id = user_id
        self.action_history = {}  # Хэш-таблица для хранения истории действий с временными метками
        self.start_work = start_work #"dd.MM.yyyy HH:mm:ss"
        self.end_work = end_work #"dd.MM.yyyy HH:mm:ss"


    def add_action(self, action: str, time: str) -> None:
        self.action_history[time] = action  # Время как ключ, действие как значение

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

class Arrow(QGraphicsItem):
    def __init__(self, node1, node2):
        super().__init__()

        self.node1 = node1  # Первый объект
        self.node2 = node2  # Второй объект

        # Сразу рисуем стрелку
        self.update_arrow()

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.darkRed, 3))
        painter.setBrush(Qt.darkRed)
        painter.drawPath(self.path)

    def update_arrow(self):
        # Получаем центры объектов
        start_center = self.node1.sceneBoundingRect().center()
        end_center = self.node2.sceneBoundingRect().center()

        # Вычисляем направление и координаты стрелки
        dx = end_center.x() - start_center.x()
        dy = end_center.y() - start_center.y()
        arrow_size = 15.0
        angle = atan2(dy, dx)

        # Координаты вершин стрелки
        arrow_p1 = QPointF(end_center.x() - arrow_size * cos(angle - pi / 6),
                           end_center.y() - arrow_size * sin(angle - pi / 6))
        arrow_p2 = QPointF(end_center.x() - arrow_size * cos(angle + pi / 6),
                           end_center.y() - arrow_size * sin(angle + pi / 6))

        # Создаем путь стрелки
        path = QPainterPath()
        path.moveTo(start_center)  # Начало линии от центра node1
        path.lineTo(end_center)    # Добавляем линию к центру node2
        path.moveTo(end_center)    # Перемещаем "ручку" для рисования к концу линии
        path.lineTo(arrow_p1)      # Линии для рисования наконечника стрелки
        path.moveTo(end_center)
        path.lineTo(arrow_p2)

        # Обновляем путь стрелки
        self.path = path
        self.update()  # Обновляем отображение стрелки


class Diamond(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.setPolygon(self.create_diamond(x, y, size))
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому ромбу

    def create_diamond(self, x, y, size):
        """Создает ромб с заданным центром (x, y) и размером."""
        half_size = size / 2
        return QtGui.QPolygonF([
            QtCore.QPointF(x, y - half_size),  # Верхняя вершина
            QtCore.QPointF(x + half_size, y),  # Правая вершина
            QtCore.QPointF(x, y + half_size),  # Нижняя вершина
            QtCore.QPointF(x - half_size, y)   # Левая вершина
        ])

    #Настройка выделения
    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем курсор на основе стороны, к которой он ближе
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.resize_side:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # super().mouseMoveEvent(event)
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.boundingRect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            center_x, center_y = rect.center().x(), rect.center().y()

            # Пропорциональное изменение размера ромба
            delta = max(abs(event.pos().x() - x), abs(event.pos().y() - y))
            new_size = max(10, delta)
            self.setPolygon(self.create_diamond(center_x, center_y, new_size))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)


class Circle(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, radius):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому кругу

    def hoverMoveEvent(self, event):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем курсор на основе стороны, к которой он ближе
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.resize_side:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
         # Обновляем привязанные стрелки, если необходимо
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            if self.resize_side in ['right', 'bottom']:
                # Пропорциональное изменение размера от правого или нижнего края
                delta = max(event.pos().x() - x, event.pos().y() - y)
                new_size = max(10, delta)  # Минимальный размер круга
                self.setRect(x, y, new_size, new_size)
            elif self.resize_side in ['left', 'top']:
                # Пропорциональное изменение размера от левого или верхнего края
                delta = max(x + w - event.pos().x(), y + h - event.pos().y())
                new_size = max(10, delta)
                new_x = x + w - new_size
                new_y = y + h - new_size
                self.setRect(new_x, new_y, new_size, new_size)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # При изменении позиции круга обновляем все привязанные стрелки
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def add_arrow(self, arrow):
        # Добавляем стрелку в список стрелок, привязанных к этому кругу
        if arrow not in self.arrows:
            self.arrows.append(arrow)
            

class Circle_2(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, radius, inner_radius_ratio=0.5):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))  # Основной круг
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому кругу

        # Создаем внутренний круг
        self.inner_radius_ratio = inner_radius_ratio  # Доля от внешнего радиуса
        self.inner_circle = QtWidgets.QGraphicsEllipseItem(self)
        self.update_inner_circle()

    def update_inner_circle(self):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        inner_radius = min(w, h) * self.inner_radius_ratio / 2
        cx, cy = x + w / 2, y + h / 2  # Центр внешнего круга
        self.inner_circle.setRect(cx - inner_radius, cy - inner_radius, 2 * inner_radius, 2 * inner_radius)
        self.inner_circle.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))  # Цвет внутреннего круга

    def hoverMoveEvent(self, event):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем курсор на основе стороны, к которой он ближе
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.resize_side:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # super().mouseMoveEvent(event)
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            if self.resize_side in ['right', 'bottom']:
                # Пропорциональное изменение размера от правого или нижнего края
                delta = max(event.pos().x() - x, event.pos().y() - y)
                new_size = max(10, delta)  # Минимальный размер круга
                self.setRect(x, y, new_size, new_size)
            elif self.resize_side in ['left', 'top']:
                # Пропорциональное изменение размера от левого или верхнего края
                delta = max(x + w - event.pos().x(), y + h - event.pos().y())
                new_size = max(10, delta)
                new_x = x + w - new_size
                new_y = y + h - new_size
                self.setRect(new_x, new_y, new_size, new_size)
            
            self.update_inner_circle()  # Обновляем внутренний круг
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

class RoundedRectangle(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, width, height, radius):
        super().__init__(x, y, width, height)
        self.width = width
        self.height = height
        self.radius = radius  # Радиус закругления
        self.setRect(x, y, width, height)
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому прямоугольнику

    def paint(self, painter, option, widget=None):
        # Устанавливаем цвет заливки
        painter.setBrush(self.brush())

        # Если элемент выбран, рисуем дополнительную рамку
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setPen(QtGui.QPen(QtCore.Qt.DashLine))  # Пунктирная линия для выделения
        else:
            painter.setPen(self.pen())  # Обычная линия

        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

    def hoverMoveEvent(self, event):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем курсор на основе стороны, к которой он ближе
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.resize_side:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # super().mouseMoveEvent(event)
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            center_x, center_y = rect.center().x(), rect.center().y()

            # Пропорциональное изменение размера прямоугольника
            if self.resize_side == 'left':
                delta = x - event.pos().x()
                new_width = max(10, w + delta)
                new_x = x - delta
                self.setRect(new_x, y, new_width, h)
            elif self.resize_side == 'right':
                delta = event.pos().x() - (x + w)
                new_width = max(10, w + delta)
                self.setRect(x, y, new_width, h)
            elif self.resize_side == 'top':
                delta = y - event.pos().y()
                new_height = max(10, h + delta)
                new_y = y - delta
                self.setRect(x, new_y, w, new_height)
            elif self.resize_side == 'bottom':
                delta = event.pos().y() - (y + h)
                new_height = max(10, h + delta)
                self.setRect(x, y, w, new_height)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)





class Ui_MainWindow(QtWidgets.QMainWindow):
    time_updated = pyqtSignal(str, str, str)  # Создаем сигнал с параметром типа str для передачи запущенного времени
    update_last_timeSW = pyqtSignal(str, str, str)  # Создаем сигнал для передачи последнего значения времени
    # Создаем сигнал для передачи данных на моменте остановки таймера
    # timeStop_ChangedSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        


    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(858, 540)
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
        self.button = QtWidgets.QPushButton(self.ToolBarBox)
        self.button.setIcon(QtGui.QIcon("imgs/decison.png"))
        self.button.setIconSize(QtCore.QSize(64, 64))  # Установка размера иконки (при необходимости)
        self.button.setObjectName("button")
        self.gridLayout.addWidget(self.button, 0, 0, 1, 1)

        # startstate.png
        self.button_2 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_2.setIcon(QtGui.QIcon("imgs/startstate.png"))
        self.button_2.setIconSize(QtCore.QSize(64, 64))
        self.button_2.setObjectName("button_2")
        self.gridLayout.addWidget(self.button_2, 0, 1, 1, 1)

        # finalstate.png
        self.button_3 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_3.setIcon(QtGui.QIcon("imgs/finalstate.png"))
        self.button_3.setIconSize(QtCore.QSize(64, 64))
        self.button_3.setObjectName("button_3")
        self.gridLayout.addWidget(self.button_3, 0, 2, 1, 1)

        # merge.png
        self.button_4 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_4.setIcon(QtGui.QIcon("imgs/merge.png"))
        self.button_4.setIconSize(QtCore.QSize(64, 64))
        self.button_4.setObjectName("button_4")
        self.gridLayout.addWidget(self.button_4, 1, 1, 1, 1)

        # Signal-sending.png
        self.button_5 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_5.setIcon(QtGui.QIcon("imgs/Signal-sending.png"))
        self.button_5.setIconSize(QtCore.QSize(64, 64))
        self.button_5.setObjectName("button_5")
        self.gridLayout.addWidget(self.button_5, 2, 0, 1, 1)

        # Signal-receipt.png
        self.button_6 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_6.setIcon(QtGui.QIcon("imgs/Signal-receipt.png"))
        self.button_6.setIconSize(QtCore.QSize(64, 64))
        self.button_6.setObjectName("button_6")
        self.gridLayout.addWidget(self.button_6, 2, 1, 1, 1)


        # arrowsolid.png
        self.button_7 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_7.setIcon(QtGui.QIcon("imgs/arrowsolid.png"))
        self.button_7.setIconSize(QtCore.QSize(64, 64))
        self.button_7.setObjectName("button_7")
        self.gridLayout.addWidget(self.button_7, 2, 2, 1, 1)

        # synchronize.png
        self.button_8 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_8.setIcon(QtGui.QIcon("imgs/synchronize.png"))
        self.button_8.setIconSize(QtCore.QSize(64, 64))
        self.button_8.setObjectName("button_8")
        self.gridLayout.addWidget(self.button_8, 1, 0, 1, 1)


        # ativestate.png
        self.button_9 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_9.setIcon(QtGui.QIcon("imgs/activestate.png"))
        self.button_9.setIconSize(QtCore.QSize(64, 64))
        self.button_9.setObjectName("button_9")
        self.gridLayout.addWidget(self.button_9, 1, 2, 1, 1)

        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.ToolBarBox)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_6.addWidget(self.graphicsView, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        #self.gridLayout_6.addWidget(self.frame, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_6, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        #Настройка главного меню
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 18))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")

        #Тестовое меню для таймера
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")


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
        self.action_Statystics = QtWidgets.QAction(MainWindow)
        self.action_Statystics.setObjectName("action_Statystics")

        #Тестовые вкладки для таймера
        self.action_time_start = QtWidgets.QAction(MainWindow)
        self.action_time_start.setObjectName("action_time_start")
        self.action_time_stop = QtWidgets.QAction(MainWindow)
        self.action_time_stop.setObjectName("action_time_stop")
        self.action_time_reset = QtWidgets.QAction(MainWindow)
        self.action_time_reset.setObjectName("action_time_reset")


        # Подключаем действие для запуска окна статистики
        self.action_Statystics.triggered.connect(self.show_static_widget)

        self.menu.addAction(self.action_4)
        self.menu.addAction(self.action)
        self.menu.addSeparator()
        self.menu.addAction(self.action_2)
        self.menu.addAction(self.action_3)
        self.menu.addSeparator()
        self.menu.addAction(self.action_PNG)
        self.menu_2.addAction(self.action_Statystics)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction()) #Тестовое меню таймера

        self.menu_3.addAction(self.action_time_start) #Добавление вкладок на тестовое меню для таймера
        self.menu_3.addAction(self.action_time_stop)
        self.menu_3.addAction(self.action_time_reset)

        # Создаём невидимый QLabel для записи времени
        self.Start_Time = QtWidgets.QLineEdit(self.centralwidget)
        self.Start_Time.setGeometry(QtCore.QRect(100, 100, 200, 50))  # Устанавливаем размер и позицию
        self.Start_Time.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
        self.Start_Time.setFont(QtGui.QFont("Helvetica", 16))  # Устанавливаем шрифт и размер
        self.Start_Time.setText("00:00:00")  # Устанавливаем начальное значение времени
        self.Start_Time.setReadOnly(True)

        # self.Start_Time.textChanged.connect(self.emit_text)


        # pixmap = QtGui.QPixmap("imgs/startstate.png")
        # if pixmap.isNull():
        #     print(f"Ошибка загрузки изображения: path/to/image.png")
        #     self.label_2.setPixmap(pixmap)
        #     self.label_2.setScaledContents(True)
        #     self.label.adjustSize()  # Автоматически настраивает размер QLabel под изображение

        #Таймер

        self.today = self.get_current_Date()
        self.time_now = self.get_current_Realtime()

        # Настраиваем второй таймер для обновления времени каждую секунду
        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.increment_time)  # Соединяем таймер с функцией обновления времени
        #self.timer_2.start(1000)  # Запускаем таймер с интервалом в 1 секунду

        #Инициализируем переменные для секундомера
        self.running = False
        self.elapsed_time = QTime(0, 0)

        self.timer = QTimer()

        self.last_time = self.Start_Time.text() # Изначальное значение времени
        self.Start_Time.setVisible(False) #По умолчанию всегда невиден
        self.timer.timeout.connect(self.update_time)

        self.start()


        #self.Start_Time.textChanged.connect(self.update_time)

        self.action_time_start.triggered.connect(self.start)
        self.action_time_stop.triggered.connect(self.stop)
        self.action_time_reset.triggered.connect(self.reset)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        # Настроим сцену для рисования
        self.scene_ = QGraphicsScene(self)
        self.graphicsView.setScene(self.scene_)

        # Кнопки тулбара
        self.button.clicked.connect(self.draw_diamond)
        self.button_2.clicked.connect(self.draw_circle)
        self.button_3.clicked.connect(self.draw_circle_2)
        self.button_9.clicked.connect(self.draw_rounded_rectangle)

        #Проверка превышение количества объектов на сцене
        self.button.clicked.connect(self.message_overcrowed_objectS)
        self.button_2.clicked.connect(self.message_overcrowed_objectS)
        self.button_3.clicked.connect(self.message_overcrowed_objectS)
        self.button_9.clicked.connect(self.message_overcrowed_objectS)

        msg = QMessageBox()
        msg.setWindowTitle("Название окна")
        msg.setText("Описание")
        msg.setIcon(QMessageBox.Warning)

        self.objectS_ = []
        self.graphicsView.setFocus()  # Устанавливаем фокус на graphicsView, чтобы горячие клавиши срабатывали
        self.connect_objectS = QShortcut(QKeySequence("Q"), self.graphicsView)
        self.connect_objectS.activated.connect(self.add_edge)

        self.connect_objectS = QShortcut(QKeySequence("D"), self.graphicsView)
        self.connect_objectS.activated.connect(self.delete_selected_item)

         # Обновляем сцену после инициализации
        self.scene_.update()  # Перерисовываем сцену


    def message_overcrowed_objectS(self):
        if len(self.objectS_) == 11:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Превышено максимальное значение элементов")
            msgBox.setWindowTitle("Предупреждение")
            msgBox.setStandardButtons(QMessageBox.Ok )
            # msgBox.buttonClicked.connect(msgButtonClick)

            returnValue = msgBox.exec()


            self.scene_.removeItem(self.objectS_[len(self.objectS_) - 1])
            self.objectS_.pop()


    def draw_diamond(self):
        # Координаты центра и размер ромба
        x, y, size = 200, 200, 50  # Пример координат и размера
        diamond = Diamond(x, y, size)
        diamond.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(diamond)  # Добавляем ромб на сцену

        self.objectS_.append(diamond)

        print("Количество объектов на сцене - ", len(self.objectS_))

        # Обновляем стрелки, если это необходимо
        for arrow in self.objectS_:
            if isinstance(arrow, Arrow):
                arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_circle(self):
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        x, y, radius = 200, 200, 30  # Пример: рисуем круг в центре с радиусом 50
        circle = Circle(x, y, radius)
        circle.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)

        print("Количество объектов на сцене - ", len(self.objectS_))

        # Обновляем стрелки, если это необходимо
        for arrow in self.objectS_:
            if isinstance(arrow, Arrow):
                arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_circle_2(self):
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        x, y, radius, into_radius = 200, 200, 30, 0.5  # Пример: рисуем круг в центре с радиусом 50
        circle = Circle_2(x,y,radius, into_radius)
        circle.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)

        print("Количество объектов на сцене - ", len(self.objectS_))

        # Обновляем стрелки, если это необходимо
        for arrow in self.objectS_:
            if isinstance(arrow, Arrow):
                arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_rounded_rectangle(self):
        # Координаты центра, ширина, высота и радиус закругления
        x, y, width, height, radius = 200, 200, 100, 60, 15  # Пример координат, размера и радиуса
        rounded_rect = RoundedRectangle(x, y, width, height, radius)
        rounded_rect.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(rounded_rect)  # Добавляем закругленный прямоугольник на сцену

        self.objectS_.append(rounded_rect)

        print("Количество объектов на сцене - ", len(self.objectS_))

        # Обновляем стрелки, если это необходимо
        for arrow in self.objectS_:
            if isinstance(arrow, Arrow):
                arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок


    def add_edge(self):
        selected_nodes = [object_ for object_ in self.objectS_ if object_.isSelected()]

        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes

            # Создаем стрелку и привязываем её к выбранным узлам
            arrow = Arrow(node1, node2)
            self.scene_.addItem(arrow)  # Добавляем стрелку на сцену

            # Привязываем стрелку к обоим кругам
            node1.add_arrow(arrow)
            node2.add_arrow(arrow)

            # Сохраняем стрелку в списке объектов
            # self.objectS_.append(arrow)
            # print("Количество объектов на сцене - ", len(self.objectS_))
            

            # Обновляем стрелку сразу после добавления
            arrow.update_arrow()  # Обновляем стрелку вручную, если нужно
            self.scene_.update()  # Перерисовываем сцену

    

    def delete_selected_item(self):
        # Получаем текущие выделенные элементы в сцене
        selected_items = self.scene_.selectedItems()

        # Удаляем каждый выделенный элемент
        for item in selected_items:
            if isinstance(item, Circle):  # Проверяем, является ли элемент кругом
                # Удаляем все стрелки, связанные с кругом, если они есть
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    for arrow in item.arrows:
                        if arrow.scene():  # Проверяем, что стрелка все еще в сцене
                            self.scene_.removeItem(arrow)
                self.scene_.removeItem(item)  # Удаляем сам круг

            if isinstance(item, Diamond):  # Проверяем, является ли элемент ромбом
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    for arrow in item.arrows:
                        if arrow.scene():  # Проверяем, что стрелка все еще в сцене
                            self.scene_.removeItem(arrow)
                self.scene_.removeItem(item) 

            if isinstance(item, Circle_2):  # Проверяем, является ли элемент кругом
                # Удаляем все стрелки, связанные с кругом, если они есть
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    for arrow in item.arrows:
                        if arrow.scene():  # Проверяем, что стрелка все еще в сцене
                            self.scene_.removeItem(arrow)
                self.scene_.removeItem(item)  # Удаляем сам круг

            if isinstance(item, RoundedRectangle):  # Проверяем, является ли элемент кругом
                # Удаляем все стрелки, связанные с кругом, если они есть
                self.objectS_.remove(item)
                if hasattr(item, 'arrows') and item.arrows:
                    for arrow in item.arrows:
                        if arrow.scene():  # Проверяем, что стрелка все еще в сцене
                            self.scene_.removeItem(arrow)
                self.scene_.removeItem(item)  # Удаляем сам круг



    #Ниже 7 функции - реализация работы таймера

    def start(self):
        if not self.running:  # Запускаем таймер, только если он не запущен
            self.running = True
            self.timer.start(1000)  # Интервал 1000 мс (1 секунда)
            self.timer_2.start(1000)  # Запускаем таймер с интервалом в 1 секунду

    def stop(self):
        if self.running:  # Останавливаем таймер
            self.running = False
            self.timer.stop()
            self.timer_2.stop()
            self.last_time = self.Start_Time.text()  # Сохраняем текущее значение времени перед остановкой

            n_datetime = QDateTime.fromString(self.change_end_time(), "dd.MM.yyyy HH:mm:ss").date().toString("dd.MM.yyyy")
            n_time = QDateTime.fromString(self.change_end_time(), "dd.MM.yyyy HH:mm:ss").time().toString("HH:mm:ss")
            print("Day is ", n_datetime, " and time is ", n_time)

            self.time_updated.emit(self.today, self.last_time, self.time_now)  # Отправляем сигнал с зафиксированным временем
            # changed_time = QDateTime.fromString(self.last_time, "HH:mm:ss")
            # print(changed_time)
            print(self.change_end_time())

    def reset(self):
        self.elapsed_time = QTime(0, 0)  # Сбрасываем время
        #self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)  # Увеличиваем время на 1 секунду
        time_str = self.elapsed_time.toString("hh:mm:ss")  # Преобразуем время в строку
        self.Start_Time.setText(time_str)  # Обновляем отображение времени
        self.last_time = time_str  # Сохраняем последнее значение времени

        # self.last_time = QDateTime.fromString(self.last_time, "HH:mm:ss").addMSecs(new_time).toString("HH:mm:ss")

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
        
        self.time_updated.emit(self.today, self.last_time, self.time_now)  # Отправляем обновленное значение
        # self.update_last_timeSW.emit(self.last_time)


    #Отображение окна статистики
    def show_static_widget(self):


        self.static_widget = QtWidgets.QWidget()  # Создаем новое окно
        self.static_ui = Ui_StaticWidget()  # Создаем экземпляр Ui_StaticWidget
        #self.static_ui = Ui_StaticWidget(self.get_last_time())   # Передаем last_time в Ui_StaticWidget

        # Подключаем слот StaticWidget к сигналу time_updated
        self.time_updated.connect(self.static_ui.update_timeworkSW)
        self.update_last_timeSW.connect(self.static_ui.update_last_timeSW)
        self.static_ui.update_timeworkSW(self.today, self.Start_Time.text(), self.time_now)
        self.static_ui.accept_today(self.today, self.time_now, self.last_time)
        self.update_last_timeSW.emit(self.today, self.last_time, self.time_now)  # Отправляем значение при открытии
        # self.static_ui.update_timeworkSW(self.last_time)
        # self.timeStop_ChangedSignal.connect(self.static_ui.receive_text)
        
        self.static_ui.setupUi(self.static_widget)  # Настраиваем новый виджет
        self.static_widget.setWindowTitle("Статистика")  # Заголовок нового окна
        self.static_widget.resize(800, 600)  # Размер нового окна
        self.static_widget.show()  # Отображаем новый виджет

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "UML editor"))
        self.ToolBarBox.setTitle(_translate("MainWindow", "Панель инструментов"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.menu_2.setTitle(_translate("MainWindow", "Статистика"))

        self.menu_3.setTitle(_translate("MainWindow", "Тест таймера"))

        self.action.setText(_translate("MainWindow", "Открыть"))
        self.action_2.setText(_translate("MainWindow", "Сохранить"))
        self.action_3.setText(_translate("MainWindow", "Сохранить как"))
        self.action_PNG.setText(_translate("MainWindow", "Экспорт в PNG"))
        self.action_4.setText(_translate("MainWindow", "Создать"))
        self.action_Statystics.setText(_translate("MainWindow", "Запустить статистику"))

        self.action_time_start.setText(_translate("MainWindow", "Запустить таймер"))
        self.action_time_stop.setText(_translate("MainWindow", "Остановить таймер"))
        self.action_time_reset.setText(_translate("MainWindow", "Сбросить таймер"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())