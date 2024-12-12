from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPen, QPainterPath, QColor, QPolygonF, QBrush, QTransform
from PyQt5.QtCore import QPointF, Qt, QLineF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPolygonItem

from math import *
import math

from PyQt5 import QtCore, QtGui, QtWidgets

global_id = 0 # Глобальный идентификатор для всех элементов
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
    def __init__(self, node1, node2, intermediate_points=None):
        super().__init__()

        self.node1 = node1  # Первый объект
        self.node2 = node2  # Второй объект
        self.intermediate_points = intermediate_points or []  # Промежуточные точки
        self.relative_points = []
        self.dragged_point_index = None
        self.top_point = None
        self.show_points = True #по умолчанию точки видны

        self.right_arrow_enabled = True
        self.left_arrow_enabled = False

        self.is_removed = False 

        self.pen_width = 3
        self.pen = QPen(Qt.darkRed, self.pen_width, Qt.SolidLine)
        self.line_type = "solid"
        self.color = Qt.darkRed  # Цвет по умолчанию
        self.update_arrow()

    def change_width(self, width): #Толщина стрелки
        self.pen_width = width
        self.pen.setWidth(self.pen_width)
        self.update()

    def boundingRect(self):
        extra_margin = 100  # Добавочная область вокруг стрелки
        rect = self.path.boundingRect()
        return rect.adjusted(-extra_margin, -extra_margin, extra_margin, extra_margin)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.pen)  # Используем pen для рисования
        painter.drawPath(self.path)

        if self.show_points:
            pen = QPen(Qt.black)
            painter.setPen(pen)
            brush = QBrush(Qt.blue)
            painter.setBrush(brush)
            for point in self.intermediate_points:
                painter.drawEllipse(point, 5, 5)

    def change_color(self, color):
        # Метод для изменения цвета стрелки
        self.pen.setColor(color)
        self.color = color  # Обновляем атрибут цвета
        self.update() 

    def change_line_type(self, line_type):
        # Метод для изменения типа линии
        if line_type == "solid":
            self.pen.setStyle(Qt.SolidLine)
        elif line_type == "dashed":
            self.pen.setStyle(Qt.DashLine)
        elif line_type == "dotted":
            self.pen.setStyle(Qt.DotLine)
        elif line_type == "dash_dot":
            self.pen.setStyle(Qt.DashDotLine)
        else:
            self.pen.setStyle(Qt.SolidLine)
        
        self.line_type = line_type
        self.update()

    def remove_arrow(self):
        if self.is_removed:
            return  # Если стрелка уже удалена, ничего не делаем

        # Удаляем стрелку из списков узлов
        if self.node1 and self in self.node1.arrows:
            self.node1.arrows.remove(self)
        if self.node2 and self in self.node2.arrows:
            self.node2.arrows.remove(self)

        # Удаляем стрелку из сцены
        self.scene().removeItem(self)

        # Обновляем флаг
        self.is_removed = True
        self.node1 = None
        self.node2 = None




    def update_arrow(self):
        if not self.node1 or not self.node2 or not self.scene():
            return

        start_center = self.node1.sceneBoundingRect().center()
        end_center = self.node2.sceneBoundingRect().center()

        node1_rect = self.node1.sceneBoundingRect()
        node2_rect = self.node2.sceneBoundingRect()

        start_point = self.get_edge_intersection(node1_rect, start_center, end_center)
        end_point = self.get_edge_intersection(node2_rect, end_center, start_center)


        if not self.relative_points:
            self.relative_points = [
                QPointF(point.x() - start_point.x(), point.y() - start_point.y())
                for point in self.intermediate_points
            ]
        self.intermediate_points = [
            QPointF(start_point.x() + rel_point.x(), start_point.y() + rel_point.y())
            for rel_point in self.relative_points
        ]

        points = [start_point] + self.intermediate_points + [end_point]
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)

        arrow_size = 15.0

        if self.right_arrow_enabled:
            angle = atan2(end_point.y() - points[-2].y(), end_point.x() - points[-2].x())
            arrow_p1 = QPointF(end_point.x() - arrow_size * cos(angle - pi / 6),
                            end_point.y() - arrow_size * sin(angle - pi / 6))
            arrow_p2 = QPointF(end_point.x() - arrow_size * cos(angle + pi / 6),
                            end_point.y() - arrow_size * sin(angle + pi / 6))
            path.moveTo(end_point)
            path.lineTo(arrow_p1)
            path.moveTo(end_point)
            path.lineTo(arrow_p2)

        if self.left_arrow_enabled:
            angle = atan2(points[1].y() - start_point.y(), points[1].x() - start_point.x()) + pi
            arrow_p1 = QPointF(start_point.x() - arrow_size * cos(angle - pi / 6),
                            start_point.y() - arrow_size * sin(angle - pi / 6))
            arrow_p2 = QPointF(start_point.x() - arrow_size * cos(angle + pi / 6),
                            start_point.y() - arrow_size * sin(angle + pi / 6))
            path.moveTo(start_point)
            path.lineTo(arrow_p1)
            path.moveTo(start_point)
            path.lineTo(arrow_p2)

        self.path = path
        self.update()


    def mousePressEvent(self, event):
        pos = event.pos()

        if event.button() == Qt.RightButton:
            # Удаление точки, если попали в существующую
            for i, point in enumerate(self.intermediate_points):
                if QLineF(pos, point).length() < 10:
                    del self.intermediate_points[i]
                    del self.relative_points[i]
                    self.update_arrow()
                    return

            # Добавление новой точки
            if self.node1:
                start_point = self.node1.sceneBoundingRect().center()
                relative_pos = QPointF(pos.x() - start_point.x(), pos.y() - start_point.y())
                self.relative_points.append(relative_pos)
                self.intermediate_points.append(pos)
                self.update_arrow()
            return

        # перетаскивание точки
        for i, point in enumerate(self.intermediate_points):
            if QLineF(pos, point).length() < 10:
                self.dragged_point_index = i
                return

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.dragged_point_index is not None:
            new_pos = event.pos()
            # Обновляем положение точки
            self.intermediate_points[self.dragged_point_index] = new_pos
            # Обновляем её относительные координаты
            start_point = self.node1.sceneBoundingRect().center()
            self.relative_points[self.dragged_point_index] = QPointF(
                new_pos.x() - start_point.x(), new_pos.y() - start_point.y()
            )
            self.update_arrow()
        else:
            super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        self.dragged_point_index = None
        super().mouseReleaseEvent(event)





    def get_side_of_intersection(self, rect, point):
        
        if abs(point.y() - rect.top()) < 1e-3:  # Верхняя сторона
            return 'top'
        elif abs(point.y() - rect.bottom()) < 1e-3:  # Нижняя сторона
            return 'bottom'
        elif abs(point.x() - rect.left()) < 1e-3:  # Левая сторона
            return 'left'
        elif abs(point.x() - rect.right()) < 1e-3:  # Правая сторона
            return 'right'
        return None  # Если не удалось определить сторону





    def get_edge_intersection(self, rect, start, end):
        # Проверяем, есть ли пересечение
        # print(f"Checking intersection: {start} -> {end} with rect {rect}")
        if rect.isNull():  
            return start

        line = QLineF(start, end)

        top_edge = QLineF(rect.topLeft(), rect.topRight())
        bottom_edge = QLineF(rect.bottomLeft(), rect.bottomRight())
        left_edge = QLineF(rect.topLeft(), rect.bottomLeft())
        right_edge = QLineF(rect.topRight(), rect.bottomRight())

        edges = [top_edge, bottom_edge, left_edge, right_edge]

        intersection_point = QPointF()
        for edge in edges:
            if line.intersect(edge, intersection_point) == QLineF.BoundedIntersection:
                # print(f"Intersection found at {intersection_point}")
                return intersection_point
        return start  # Возвращаем начальную точку, если нет пересечений





class Decision(QtWidgets.QGraphicsPolygonItem):
    _id_counter = 0
    def __init__(self, x, y, size, color=QtCore.Qt.white, node1=None, node2=None):
        super().__init__()
        global global_id  # Объявляем, что будем использовать глобальную переменную
        self.unique_id = global_id - 8
        global_id += 1
        self.size = size
        self.center_x = x  # Сохраняем центр при инициализации
        self.center_y = y
        self.color = color
        self.border_color = QtCore.Qt.black  # Цвет окантовки
        self.setPolygon(self.create_diamond(self.center_x, self.center_y, self.size))
        self.setBrush(self.color)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения
        self.setPen(QtGui.QPen(self.border_color, 2))

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому ромбу

        self.node1 = node1
        self.node2 = node2

    def clone(self):
        clone_item = Decision(self.center_x, self.center_y, self.size)
        clone_item.setPolygon(self.polygon())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        return clone_item

    def create_diamond(self, x, y, size):
        # Создает ромб с заданным центром (x, y) и размером.
        half_size = size / 2
        return QtGui.QPolygonF([
            QtCore.QPointF(x, y - half_size),  # Верхняя вершина
            QtCore.QPointF(x + half_size, y),  # Правая вершина
            QtCore.QPointF(x, y + half_size),  # Нижняя вершина
            QtCore.QPointF(x - half_size, y)   # Левая вершина
        ])

    def setColor(self, color):  
        self.color = color
        print(color)
        self.setBrush(self.color)
        self.update()  # Обновляем элемент для перерисовки


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
        if event.button() == QtCore.Qt.RightButton:  # Проверяем нажатие ПКМ
            color = QtWidgets.QColorDialog.getColor()
            if color.isValid():
                self.setColor(color)  # Устанавливаем выбранный цвет

    def mouseMoveEvent(self, event):
        # Обновляем стрелки при движении объекта
        for arrow in self.arrows:
            arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом

        if self.is_resizing:
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)
            delta = max(delta_x, delta_y) * 2  # Умножаем на 2, чтобы изменить размер симметрично

            new_size = max(10, delta)  # Минимальный размер 10
            self.size = new_size  # Обновляем атрибут размера
            self.setPolygon(self.create_diamond(self.center_x, self.center_y, new_size))
        else:
            super().mouseMoveEvent(event)



    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # # Сглаживание отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений


    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)
            arrow.update_arrow()



class StartEvent(QtWidgets.QGraphicsEllipseItem):
    _id_counter = 0
    def __init__(self, x, y, radius, color=QtCore.Qt.black, node1=None, node2=None):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        global global_id  # Объявляем, что будем использовать глобальную переменную
        self.unique_id = global_id - 8
        global_id += 1
        self.x_center = x
        self.y_center = y
        self.radius = radius
        self.color = color
        self.setBrush(color)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому кругу

        self.node1 = node1
        self.node2 = node2

    # def remove_all_arrows(self):
    #     for arrow in list(self.arrows):  # Создаем копию списка для безопасного удаления
    #         if arrow.scene():
    #             arrow.remove_arrow()  # Удаляем стрелку
    #     self.arrows.clear()  # Очищаем список стрелок

    def clone(self):
        clone_item = StartEvent(self.x_center, self.y_center, self.radius)
        clone_item.setRect(self.rect())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        clone_item.radius = self.radius
        return clone_item


    def setRadius(self, new_radius):
        self.radius = new_radius
        self.setRect(self.x(), self.y(), new_radius * 2, new_radius * 2)

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

    # Сглаживание отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        # self.arrows.append(arrow)
        # Добавляем стрелку в список стрелок, привязанных к этому кругу
        if arrow not in self.arrows:
            self.arrows.append(arrow)

#Дочерний элемент(внтуренний круг) EndEvent
class InnerCircle(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        print(f"Родитель - {self.parentItem()}")

    def paint(self, painter, option, widget):
        # Включаем сглаживание
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)
            

class EndEvent(QtWidgets.QGraphicsEllipseItem):
    _id_counter = 0
    def __init__(self, x, y, radius, inner_radius_ratio=0.5, color=QtCore.Qt.white, node1=None, node2=None):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        # EndEvent._id_counter += 1
        self.x_center = x
        self.y_center = y
        self.radius = radius
        self.inner_radius_ratio = inner_radius_ratio
        self.color = color
        self.setBrush(color)  # Основной круг
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)  # Позволяет перемещать элемент
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому кругу

        # Создаем внутренний круг
        self.inner_radius_ratio = inner_radius_ratio  # Доля от внешнего радиуса
        self.inner_circle = InnerCircle(self)
        self.update_inner_circle()

    def clone(self):
        clone_item = EndEvent(self.x_center, self.y_center, self.radius, self.inner_radius_ratio)
        clone_item.setRect(self.rect())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        clone_item.radius = self.radius
        clone_item.inner_radius_ratio = self.inner_radius_ratio
        clone_item.update_inner_circle()
        return clone_item

    def setRadius(self, new_radius):
        self.radius = new_radius
        self.setRect(self.x(), self.y(), new_radius * 2, new_radius * 2)

    def update_inner_circle(self):
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        inner_radius = min(w, h) * self.inner_radius_ratio / 2
        cx, cy = x + w / 2, y + h / 2  # Центр внешнего круга
        self.inner_circle.setRect(cx - inner_radius, cy - inner_radius, 2 * inner_radius, 2 * inner_radius)

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

    # Сглаживание отрисовки объекта
    def paint(self, painter, option, widget):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)


    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

class Text_into_object(QtWidgets.QGraphicsTextItem):
    def __init__(self, max_length, parent=None):
        super().__init__(parent)
        self.unique_id = None
        self.max_length = max_length

    def keyPressEvent(self, event):

        current_text = self.toPlainText()

        if len(current_text) >= self.max_length and event.key() not in (
            QtCore.Qt.Key_Backspace,
            QtCore.Qt.Key_Delete,
            QtCore.Qt.Key_Left,
            QtCore.Qt.Key_Right,
        ):
            event.ignore()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        # При потере фокуса выключаем редактирование
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        super().focusOutEvent(event)
        
    def update_wrapped_text(self, max_width):
        font_metrics = QtGui.QFontMetrics(self.font())
        current_text = self.toPlainText()
        words = current_text.split()
        current_line = ""
        wrapped_text = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font_metrics.width(test_line) <= max_width:
                current_line = test_line
            else:
                wrapped_text += f"{current_line}\n"
                current_line = word

        wrapped_text += current_line
        self.setPlainText(wrapped_text)


class ActiveState(QtWidgets.QGraphicsRectItem):
    _id_counter = 0
    def __init__(self, x, y, width, height, radius, color=QtCore.Qt.white, node1=None, node2=None):
        super().__init__(x, y, width, height)
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        self.x_center = x
        self.y_center = y
        self.width = width
        self.height = height
        self.radius = radius  # Радиус закругления
        self.color = color
        self.setRect(self.x_center, self.y_center, width, height)
        self.setBrush(color)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)  # Для отслеживания наведения

        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к этому прямоугольнику

        # Создаем текстовое поле внутри объекта
        self.text_item = Text_into_object(15, self) #15 - это максимально разрешаеммая длинна ввода
        self.text_item.setPlainText("Текст")
        self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.update_text_wrap()
        self.update_text_position()

    def clone(self):
        cloned_item = ActiveState(self.x_center, self.y_center, self.width, self.height, self.radius)
        cloned_item.setRect(self.rect())
        cloned_item.setBrush(self.brush())
        cloned_item.setPen(self.pen())
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())

        return cloned_item

    def update_text_wrap(self):
        rect = self.rect()
        text_width = rect.width() - 10  # Отступы по 5px с каждой стороны
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

        # self.max_text_length = 15 

    def update_text_position(self):
        rect = self.rect()
        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()

        center_x = rect.x() + rect.width() / 2
        center_y = rect.y() + rect.height() / 2

        # Устанавливаем текст по центру
        self.text_item.setPos(center_x - text_width / 2, center_y - text_height / 2)



    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)  # Включение сглаживания
        # Устанавливаем цвет заливки
        painter.setBrush(self.brush())

        # Если элемент выбран, рисуем дополнительную рамку
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setPen(QtGui.QPen(QtCore.Qt.DashLine))  # Пунктирная линия для выделения
        else:
            painter.setPen(self.pen())  # Обычная линия

        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

        # painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # super().paint(painter, option, widget)

    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Проверяем углы
        if abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))  # Верхний левый угол
            self.resize_side = 'top_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))  # Верхний правый угол
            self.resize_side = 'top_right'
        elif abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))  # Нижний левый угол
            self.resize_side = 'bottom_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))  # Нижний правый угол
            self.resize_side = 'bottom_right'
        # Проверяем стороны
        elif abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))  # Левая сторона
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))  # Правая сторона
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))  # Верхняя сторона
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))  # Нижняя сторона
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


    #Пока не работает. вернуться к этому
    def mouseDoubleClickEvent(self, event):
        print("Произошел двойной клик по элементу")
        # Если двойной клик произошёл на текстовом элементе, включаем редактирование
        local_pos = self.mapToItem(self.text_item, event.pos())
        if self.text_item.contains(local_pos):
            self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            self.text_item.setFocus(QtCore.Qt.MouseFocusReason)
        else:
            super().mouseDoubleClickEvent(event)



    def mouseMoveEvent(self, event):

        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            # Проверка нажатия клавиши Shift
            is_shift_pressed = QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.ShiftModifier

            delta_x = event.pos().x() - (x if self.resize_side in ['top_left', 'bottom_left', 'left'] else (x + w))
            delta_y = event.pos().y() - (y if self.resize_side in ['top_left', 'top_right', 'top'] else (y + h))

            if self.resize_side == 'top_left':
                new_width = max(10, w - delta_x)
                new_height = max(10, h - delta_y)
                if new_width > 10 and new_height > 10:
                    self.setRect(x + delta_x, y + delta_y, new_width, new_height)

            elif self.resize_side == 'top_right':
                if is_shift_pressed:
                    scale_factor = max(delta_x / w, -delta_y / h)
                    delta_x = scale_factor * w
                    delta_y = -scale_factor * h
                new_width = max(10, w + delta_x)
                new_height = max(10, h - delta_y)
                if new_width > 10 and new_height > 10:
                    self.setRect(x, y + delta_y, new_width, new_height)

            elif self.resize_side == 'bottom_left':
                if is_shift_pressed:
                    scale_factor = max(-delta_x / w, delta_y / h)
                    delta_x = -scale_factor * w
                    delta_y = scale_factor * h
                new_width = max(10, w - delta_x)
                new_height = max(10, h + delta_y)
                if new_width > 10 and new_height > 10:
                    self.setRect(x + delta_x, y, new_width, new_height)

            elif self.resize_side == 'bottom_right':
                new_width = max(10, w + delta_x)
                new_height = max(10, h + delta_y)
                if new_width > 10 and new_height > 10:
                    self.setRect(x, y, new_width, new_height)

            elif self.resize_side == 'left':
                new_width = max(10, w - delta_x)
                if is_shift_pressed:
                    new_height = new_width * (h / w)
                    if new_height > 10:
                        self.setRect(x + delta_x, y, new_width, new_height)
                else:
                    if new_width > 10:
                        self.setRect(x + delta_x, y, new_width, h)

            elif self.resize_side == 'right':
                new_width = max(10, w + delta_x)
                if is_shift_pressed:
                    new_height = new_width * (h / w)
                    if new_height > 10:
                        self.setRect(x, y, new_width, new_height)
                else:
                    self.setRect(x, y, new_width, h)

            elif self.resize_side == 'top':
                new_height = max(10, h - delta_y)
                if is_shift_pressed:
                    new_width = new_height * (w / h)
                    if new_width > 10:
                        self.setRect(x, y + delta_y, new_width, new_height)
                else:
                    if new_height > 10:
                        self.setRect(x, y + delta_y, w, new_height)

            elif self.resize_side == 'bottom':
                new_height = max(10, h + delta_y)
                if is_shift_pressed:
                    new_width = new_height * (w / h)
                    if new_width > 10:
                        self.setRect(x, y, new_width, new_height)
                else:
                    self.setRect(x, y, w, new_height)

            # Обновляем текст
            self.update_text_position()
            self.update_text_wrap()
        else:
            super().mouseMoveEvent(event)



    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:         
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позици
               
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)



class SignalSending(QtWidgets.QGraphicsPolygonItem):
    _id_counter = 0
    def __init__(self, x, y, width, height, color=QtCore.Qt.white, node1=None, node2=None):
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        super().__init__()
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.color = color

        # Создаем пентагон
        self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.width, self.height))
        self.setBrush(color)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении положения
        self.setAcceptHoverEvents(True)

        self.is_resizing = False # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10 # Чувствительная область для изменения размера
        self.current_reflection = "None" #Отражение объекта
        self.current_reflection = "Справа"

        self.arrows = []
        self.text_item = Text_into_object(15, self)
        self.text_item.setPlainText("Signal Sending")
        self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.text_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.update_text_wrap()
        self.update_text_position()

    # def update_size(self, new_width, new_height):
    #     self.width = new_width
    #     self.height = new_height
    #     self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.width, self.height))
    #     self.update_text_wrap()
    #     self.update_text_position()

    def clone(self):
        cloned_item = SignalSending(self.center_x, self.center_y, self.width, self.height)
        cloned_item.setPolygon(self.polygon())
        cloned_item.setBrush(self.brush())
        cloned_item.setPen(self.pen())
        
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())

        return cloned_item

    def update_text_wrap(self):
        rect = self.boundingRect()
        text_width = rect.width() - 10
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

    def create_pentagon(self, x, y, width, height):
        # Создает прямоугольный пятиугольник с заданным центром (x, y) и размером.
        points = [
            QtCore.QPointF(x - width / 2, y),          # Середина слева
            QtCore.QPointF(x + width / 2, y),          # Середина справа
            QtCore.QPointF(x + width*0.7, y - height / 2),             # Середина внизу
            QtCore.QPointF(x + width / 2, y - height),   # Нижний левый угол
            QtCore.QPointF(x - width / 2, y - height)          # Середина слева
        ]

        polygon = QtGui.QPolygonF(points)

        return polygon

    def update_text_position(self):
        center_x = self.center_x
        center_y = self.center_y - self.height / 2 

        # Центрируем текст относительно вычисленного центра
        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()

        if self.current_reflection == "Справа":
            self.text_item.setPos(
                center_x - text_width / 2,
                center_y + text_height / 2
            )
        else:
            self.text_item.setPos(
                center_x + text_width / 2,
                center_y - text_height / 2
            )

    def reflect(self, direction):
        # Устанавливаем текущее направление отражения
        self.current_reflection = direction

        # Получаем текущий центр объекта в сцене
        original_scene_center = self.sceneBoundingRect().center()

        # Создаем трансформацию для отражения
        transform = QTransform()
        if direction == "Слева":  # Отразить по вертикальной оси
            transform.scale(-1, 1)  # Инвертировать по оси X
        elif direction == "Справа":  # Отразить по горизонтальной оси
            transform.scale(1, -1)  # Инвертировать по оси Y
        else:
            return  # Не менять ничего

        # Применяем трансформацию
        self.setTransform(transform, combine=False)

        # Корректируем положение объекта, чтобы сохранить его центр
        new_scene_center = self.sceneBoundingRect().center()
        delta_x = original_scene_center.x() - new_scene_center.x()
        delta_y = original_scene_center.y() - new_scene_center.y()
        self.moveBy(delta_x, delta_y)

        # Принудительно обновляем текстовую позицию
        self.text_item.setTransform(QTransform())  # Сбрасываем влияние трансформации
        self.update_text_position()

    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

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
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        for arrow in self.arrows:
            arrow.update_arrow()
        
        if self.is_resizing:
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)

            if self.resize_side in ['left', 'right']:
                new_width = max(10, delta_x * 2)
                self.width = new_width
            if self.resize_side in ['top', 'bottom']:
                new_height = max(10, delta_y * 2)
                self.height = new_height

            new_polygon = self.create_pentagon(self.center_x, self.center_y, self.width, self.height)
            self.setPolygon(new_polygon)
            self.update_text_wrap()
            self.update_text_position()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)
        
    #Сглаживаине отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        self.arrows.append(arrow)



class SignalReceipt(QtWidgets.QGraphicsPolygonItem):
    _id_counter = 0
    def __init__(self, x, y, width, height, color=QtCore.Qt.white, node1=None, node2=None):
        super().__init__()
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.color=color

        # Создаем пентагон
        self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.width, self.height))
        self.setBrush(color)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)  # Отправляет события об изменении 
        self.setAcceptHoverEvents(True)

        self.is_resizing = False # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10 # Чувствительная область для изменения размера
        self.current_reflection = "None" #Отражение объекта
        self.current_reflection = "Слева"

        self.arrows = []

        self.text_item = Text_into_object(15, self)
        self.text_item.setPlainText("Signal receipt")
        self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.text_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.update_text_wrap()
        self.update_text_position()

    def clone(self):
        cloned_item = SignalSending(self.center_x, self.center_y, self.width, self.height)
        cloned_item.setPolygon(self.polygon())
        cloned_item.setBrush(self.brush())
        cloned_item.setPen(self.pen())
        
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())

        return cloned_item

    def update_text_wrap(self):
        rect = self.boundingRect()
        text_width = rect.width() - 10
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

    def create_pentagon(self, x, y, width, height):
        # Создает прямоугольный пятиугольник с заданным центром (x, y) и размером.
        points = [
            QtCore.QPointF(x + width * (-0.325), y - height / 2), # Угол слева
            QtCore.QPointF(x - width / 2, y),          # Первая точка
            QtCore.QPointF(x + width / 2, y),          # Точка напротив неё
            QtCore.QPointF(x + width / 2, y - height),   # Первая нижняя точка
            QtCore.QPointF(x - width / 2, y - height)    # Точка напротив неё
        ]

        polygon = QtGui.QPolygonF(points)


        return polygon

    def update_text_position(self):
        center_x = self.center_x
        center_y = self.center_y - self.height / 2 

        # Центрируем текст относительно вычисленного центра
        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()

        if self.current_reflection == "Слева":
            self.text_item.setPos(
                center_x - text_width / 2,
                center_y + text_height / 2
            )
        else:
            self.text_item.setPos(
                center_x + text_width / 2,
                center_y - text_height / 2
            )

    def reflect(self, direction):
        # Устанавливаем текущее направление отражения
        self.current_reflection = direction

        # Получаем текущий центр объекта в сцене
        original_scene_center = self.sceneBoundingRect().center()

        # Создаем трансформацию для отражения
        transform = QTransform()
        if direction == "Слева":  # Отразить по вертикальной оси
            transform.scale(1, -1)  # Инвертировать по оси X
        elif direction == "Справа":  # Отразить по горизонтальной оси
            transform.scale(-1, 1)  # Инвертировать по оси Y
        else:
            return  # Не менять ничего

        # Применяем трансформацию
        self.setTransform(transform, combine=False)

        # Корректируем положение объекта, чтобы сохранить его центр
        new_scene_center = self.sceneBoundingRect().center()
        delta_x = original_scene_center.x() - new_scene_center.x()
        delta_y = original_scene_center.y() - new_scene_center.y()
        self.moveBy(delta_x, delta_y)

        # Принудительно обновляем текстовую позицию
        # self.text_item.setTransform(QTransform())  # Сбрасываем влияние трансформации
        self.update_text_position()

    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

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
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        for arrow in self.arrows:
            arrow.update_arrow()
        if self.is_resizing:
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)

            if self.resize_side in ['left', 'right']:
                new_width = max(10, delta_x * 2)
                self.width = new_width
            if self.resize_side in ['top', 'bottom']:
                new_height = max(10, delta_y * 2)
                self.height = new_height

            self.update_text_position()
            self.update_text_wrap()
            new_polygon = self.create_pentagon(self.center_x, self.center_y, self.width, self.height)
            self.setPolygon(new_polygon)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # #Сглаживаине отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        self.arrows.append(arrow)

class Splitter_Merge(QtWidgets.QGraphicsPolygonItem):
    _id_counter = 0
    def __init__(self, x, y, width, height, rot, node1=None, node2=None):
        super().__init__()
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.rot = rot

        self.setPolygon(self.create_SM(self.center_x, self.center_y, self.width, self.height))

        self.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        rect = self.boundingRect()
        self.setTransformOriginPoint(self.center_x, self.center_y) #Центируем точки при смене ориентации


        self.is_resizing = False # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None # Определяем, с какой стороны идет изменение размера
        self.resize_margin = 10 # Чувствительная область для изменения размера


        self.arrows = []

    def clone(self):
        clone_item = Splitter_Merge(self.center_x, self.center_y, self.width, self.height)
        clone_item.setPolygon(self.polygon())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        return clone_item

    def create_SM(self, x, y, width, height):
        # Создает прямоугольный пятиугольник с заданным центром (x, y) и размером.
        points = [
            QtCore.QPointF(x - width / 2, y),          # Первая точка
            QtCore.QPointF(x + width / 2, y),          # Точка напротив неё
            QtCore.QPointF(x + width / 2, y - height / 2),   # Первая нижняя точка
            QtCore.QPointF(x - width / 2, y - height / 2)    # Точка напротив неё
        ]

        sm = QtGui.QPolygonF(points)


        return sm

    #Обновляем ориентацию объекта через панель редактирования
    def update_size_and_orientation(self, width, height, rotation):
        self.setPolygon(self.create_SM(self.center_x, self.center_y, width, height))
        self.setRotation(rotation)
        self.rot = rotation
        self.update()


    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.resize_side = 'right'
        # elif abs(event.pos().y() - y) <= self.resize_margin:
        #     self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        #     self.resize_side = 'top'
        # elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
        #     self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        #     self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        for arrow in self.arrows:
            arrow.update_arrow()
        if self.is_resizing:
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)

            if self.resize_side in ['left', 'right']:
                new_width = max(10, delta_x * 2)
                self.width = new_width
            if self.resize_side in ['top', 'bottom']:
                new_height = max(10, delta_y * 2)
                self.height = new_height

            new_polygon = self.create_SM(self.center_x, self.center_y, self.width, self.height)
            self.setPolygon(new_polygon)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # #Сглаживаине отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)


    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    def add_arrow(self, arrow):
        self.arrows.append(arrow)

class ImageItem(QtWidgets.QGraphicsPixmapItem):
    _id_counter = 0
    def __init__(self, pixmap, x, y):
        super().__init__(pixmap)
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        self.x_center = x
        self.y_center = y
        self.setPos(self.x_center, self.y_center)  # Устанавливаем начальную позицию
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable |
            QtWidgets.QGraphicsItem.ItemIsSelectable |
            QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)  # Разрешаем обработку событий наведения

        self.is_resizing = False  # Флаг изменения размера
        self.resize_margin = 10  # Зона, в которой можно начинать изменение размера
        self.arrows = []  # Список стрелок, привязанных к изображению

    def clone(self):
        cloned_item = ImageItem(self.pixmap(), self.x_center, self.y_center)
        cloned_item.setOpacity(self.opacity())
        return cloned_item

    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Изменяем курсор при наведении на края изображения
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
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if self.cursor().shape() in [QtCore.Qt.SizeHorCursor, QtCore.Qt.SizeVerCursor]:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    #     if self.is_resizing:
    #         rect = self.boundingRect()
    #         delta = event.pos() - rect.center()
    #         new_width = max(10, rect.width() + delta.x() * 2)  # Минимальная ширина 10
    #         new_height = max(10, rect.height() + delta.y() * 2)  # Минимальная высота 10

    #         # Обновляем размер изображения
    #         self.setPixmap(
    #             self.pixmap().scaled(int(new_width), int(new_height), QtCore.Qt.KeepAspectRatio)
    #         )
    #     else:
    #         super().mouseMoveEvent(event)

        # Обновляем стрелки
        for arrow in self.arrows:
            arrow.update_arrow()

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        """Сглаживание при отрисовке."""
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        super().paint(painter, option, widget)


class Text_Edit(Text_into_object):
    _id_counter = 0
    def __init__(self, x, y, width, height, text="Текст", max_length=250, parent=None):
        super().__init__(max_length, parent)
        global global_id
        self.unique_id = global_id - 8
        global_id += 1
        self.setPlainText(text)
        self.max_length = max_length

        self.x_center = x
        self.y_center = y
        self.arrows = []

        self.setPos(self.x_center, self.y_center)
        self.setFont(QtGui.QFont("Arial", 12))
        self.setDefaultTextColor(QtGui.QColor(0, 0, 0))

        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setAcceptHoverEvents(True)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self.is_resizing = False
        self.resize_margin = 10
        self.resize_side = None

        self.width = width
        self.height = height

    def clone(self):
        cloned_item = Text_Edit(self.x_center, self.y_center, self.width, self.height, self.toPlainText())
        
        return cloned_item

    def update_text_wrap(self):
        rect = self.boundingRect()
        max_width = rect.width() - 10
        if max_width > 0:
            super().update_wrapped_text(max_width)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setFocus(QtCore.Qt.MouseFocusReason)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def hoverMoveEvent(self, event):
        rect = self.boundingRect() 
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))  # Верхний левый угол
            self.resize_side = 'top_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))  # Верхний правый угол
            self.resize_side = 'top_right'
        elif abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))  # Нижний левый угол
            self.resize_side = 'bottom_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))  # Нижний правый угол
            self.resize_side = 'bottom_right'
        elif abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))  # Левая сторона
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))  # Правая сторона
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))  # Верхняя сторона
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))  # Нижняя сторона
            self.resize_side = 'bottom'
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.resize_side = None

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
            rect = self.boundingRect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            delta_x = event.pos().x() - event.lastPos().x()
            delta_y = event.pos().y() - event.lastPos().y()

            new_x, new_y = self.pos().x(), self.pos().y()
            new_width, new_height = self.width, self.height

            if self.resize_side in ['top_left', 'left', 'bottom_left']:
                new_width = max(10, self.width - delta_x)
                new_x += delta_x
            if self.resize_side in ['top_left', 'top', 'top_right']:
                new_height = max(10, self.height - delta_y)
                new_y += delta_y
            if self.resize_side in ['top_right', 'right', 'bottom_right']:
                new_width = max(10, self.width + delta_x)
            if self.resize_side in ['bottom_left', 'bottom', 'bottom_right']:
                new_height = max(10, self.height + delta_y)
            self.prepareGeometryChange()
            self.width = new_width
            self.height = new_height
            self.setPos(new_x, new_y)

            # Обновляем ширину текста
            self.setTextWidth(self.width)
            self.update_text_wrap()
        else:
            super().mouseMoveEvent(event)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)    