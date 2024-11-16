from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPen, QPainterPath, QColor
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPolygonItem

from math import *
import math

from PyQt5 import QtCore, QtGui, QtWidgets

# class Text_Edit(QtWidgets.QGraphicsTextItem):
#     def __init__(self, x, y, width, height, text=""):
#         super().__init__(text)  # Инициализация с начальным текстом
#         self.setPos(x, y)  # Устанавливаем позицию текста
#         self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)  # Разрешаем редактирование текста
#         self.setTextWidth(width)  # Устанавливаем ширину текста
#         self.setDefaultTextColor(QtGui.QColor(0, 0, 0))  # Цвет текста (по умолчанию черный)
#         self.setFont(QtGui.QFont("Arial", 12))  # Шрифт текста
#
#         # Создаем прямоугольник, который будет служить фоном для текстового поля
#         self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
#         self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события изменения положения
#
#         self.setAcceptHoverEvents(True)  # Для отслеживания наведения
#
#         self.resize_margin = 10  # Чувствительная область для изменения размера
#         self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
#         self.resize_side = None  # Определяем, с какой стороны идет изменение размера
#
#     def hoverMoveEvent(self, event):
#         rect = self.boundingRect()
#         x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
#
#         # Определяем курсор на основе стороны, к которой он ближе
#         if abs(event.pos().x() - x) <= self.resize_margin:
#             self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
#             self.resize_side = 'left'
#         elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
#             self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
#             self.resize_side = 'right'
#         elif abs(event.pos().y() - y) <= self.resize_margin:
#             self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
#             self.resize_side = 'top'
#         elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
#             self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
#             self.resize_side = 'bottom'
#         else:
#             self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
#             self.resize_side = None
#         super().hoverMoveEvent(event)
#
#     def mousePressEvent(self, event):
#         if self.resize_side:
#             self.is_resizing = True
#         else:
#             self.is_resizing = False
#         super().mousePressEvent(event)
#
#     def mouseMoveEvent(self, event):
#         if self.is_resizing:
#             rect = self.boundingRect()
#             x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
#
#             if self.resize_side == 'right':
#                 delta = event.pos().x() - (x + w)
#                 new_width = max(10, w + delta)
#                 self.setTextWidth(new_width)
#             elif self.resize_side == 'left':
#                 delta = x - event.pos().x()
#                 new_width = max(10, w + delta)
#                 new_x = x + w - new_width
#                 self.setPos(new_x, y)
#                 self.setTextWidth(new_width)
#             elif self.resize_side == 'bottom':
#                 delta = event.pos().y() - (y + h)
#                 new_height = max(10, h + delta)
#                 self.setTextHeight(new_height)
#             elif self.resize_side == 'top':
#                 delta = y - event.pos().y()
#                 new_height = max(10, h + delta)
#                 new_y = y + h - new_height
#                 self.setPos(x, new_y)
#                 self.setTextHeight(new_height)
#
#         else:
#             super().mouseMoveEvent(event)
#
#     def mouseReleaseEvent(self, event):
#         self.is_resizing = False
#         super().mouseReleaseEvent(event)
#
#     def setTextHeight(self, height):
#         rect = self.boundingRect()
#         self.setTextWidth(rect.width())  # Фиксируем ширину
#         self.setTextHeight(height)  # Устанавливаем новую высоту
#
#     def setTextWidth(self, width):
#         rect = self.boundingRect()
#         self.setTextWidth(width)  # Устанавливаем новую ширину


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
        self.center_x = x  # Сохраняем центр при инициализации
        self.center_y = y
        self.setPolygon(self.create_diamond(self.center_x, self.center_y, self.size))
        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому ромбу

    def create_diamond(self, x, y, size):
        # Создает ромб с заданным центром (x, y) и размером.
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
            # Пропорциональное изменение размера ромба, оставляя центр фиксированным
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)
            delta = max(delta_x, delta_y) * 2  # Умножаем на 2, чтобы изменить размер симметрично

            new_size = max(10, delta)  # Минимальный размер 10
            self.setPolygon(self.create_diamond(self.center_x, self.center_y, new_size))
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
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому прямоугольнику

        # Создаем текстовое поле внутри объекта
        self.text_item = QtWidgets.QGraphicsTextItem(self)
        self.text_item.setPlainText("Текст")
        self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)  # Разрешаем редактирование текста
        self.text_item.setPos(x + width / 4, y + height / 4)  # Устанавливаем начальную позицию текста

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
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            self.text_item.setPos(rect.x() + w / 4, rect.y() + h / 4)  # Обновляем позицию текста

            # Пропорциональное изменение размера прямоугольника
            if self.resize_side == 'left':
                delta = x - event.pos().x()
                new_width = max(10, w + delta)
                # Зафиксировать положение X, изменить только ширину
                self.setRect(x - delta, y, new_width, h)
            elif self.resize_side == 'right':
                delta = event.pos().x() - (x + w)
                new_width = max(10, w + delta)
                self.setRect(x, y, new_width, h)  # Изменяется только ширина
            elif self.resize_side == 'top':
                delta = y - event.pos().y()
                new_height = max(10, h + delta)
                # Зафиксировать положение Y, изменить только высоту
                self.setRect(x, y - delta, w, new_height)
            elif self.resize_side == 'bottom':
                delta = event.pos().y() - (y + h)
                new_height = max(10, h + delta)
                self.setRect(x, y, w, new_height)  # Изменяется только высота
        else:
            # Если идет изменение размера, не разрешаем перемещать
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Предотвращаем перемещение элемента при изменении размера
            if self.is_resizing:
                self.pos()  # Зафиксировать позицию
        return super().itemChange(change, value)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)



class SignalSending(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.center_x = x  # Сохраняем центр при инициализации
        self.center_y = y

        # Создаем пентагон с отражением сразу при его создании
        self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.size))

        self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому пентагону

    def create_pentagon(self, x, y, size):
        # Создает прямоугольный пятиугольник с заданным центром (x, y) и размером.
        points = []
        
        # Первая горизонтальная сторона (слева направо)
        points.append(QtCore.QPointF(x - size / 2, y))
        points.append(QtCore.QPointF(x + size / 2, y))
        
        # Второй угол (вниз)
        points.append(QtCore.QPointF(x + size / 2, y + size / 2))
        
        # Третий угол (вправо и вверх)
        points.append(QtCore.QPointF(x, y + size))
        
        # Четвертая сторона (вверх и влево, закрывает фигуру)
        points.append(QtCore.QPointF(x - size / 2, y + size / 2))

        polygon = QtGui.QPolygonF(points)

        # Применяем отражение по горизонтали и поворот на 90 градусов при создании полигона
        transform = QtGui.QTransform()
        transform.translate(self.center_x, self.center_y)  # Переводим систему координат в центр полигона
        transform.scale(-1, 1)  # Отражение по оси X
        transform.rotate(90)  # Поворот на 90 градусов
        transform.translate(-self.center_x, -self.center_y)  # Возвращаем систему координат в исходное положение

        # Поскольку полигон по умолчаю создается так, что острый угол у него находится внизу, а сторона
        # с прямыми углами в верху, то мы его переворачиваем
        reflected_rotated_polygon = QtGui.QPolygonF([transform.map(point) for point in polygon])

        return reflected_rotated_polygon

    # Настройка выделения
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
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            # Пропорциональное изменение размера пентагона, оставляя центр фиксированным
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)
            delta = max(delta_x, delta_y) * 2  # Умножаем на 2, чтобы изменить размер симметрично

            new_size = max(10, delta)  # Минимальный размер 10
            new_polygon = self.create_pentagon(self.center_x, self.center_y, new_size)
            self.setPolygon(new_polygon)
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


