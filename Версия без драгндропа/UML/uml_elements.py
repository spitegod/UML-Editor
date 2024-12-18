from math import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPointF, QLineF, QEvent
from PyQt5.QtGui import QPen, QPainterPath, QColor, QPolygonF, QBrush, QTransform, QPainter, QCursor
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPolygonItem

GLOBAL_ID = 0 # Глобальный идентификатор для всех элементов

'''Класс стрелки'''
class Arrow(QGraphicsItem):
    def __init__(self, node1, node2, intermediate_points=None):
        super().__init__()

        '''Начальные данные'''
        self.node1 = node1  # Первый соединенный объект
        self.node2 = node2  # Второй соединенный объект
        self.intermediate_points = intermediate_points or []  # Список промежуточные точкек 
        # Примечание: Сначало стрелка рисуется без точек, всегда
        self.setFlags(QGraphicsItem.ItemIsSelectable) # Возможность выбора стрелки

        self.relative_points = []       # Список относительных точек. По факту используется
                                        # как временная копия intermediate_point при передвижении стрелки
        self.dragged_point_index = None # Индекс перетаскиваемой точки
        self.is_removed = False         # Флаг, проверяющий удалена ли стрелка (А также принадлежит ли стрелка сцене)

        '''Визуальные параметры стрелки для панели редактирования'''
        self.show_points = True     # Параметр видимость точек на стрелке. По умолчанию точки видны
        self.line_type = "solid"    # Параметр тип линии стрекли. По умолчанию стрекла сплошная
        self.color = Qt.darkRed     # Параметр цвета стрекли. По умолчанию стрелка темно-красная
        self.pen_width = 3          # Параметр толщины стрелки. По умолчанию стрелка рисуется толщиной в 3 пикселя

        '''Флаги расположения наконечника'''
        self.right_arrow_enabled = True # По умолчанию наконечник рисуется справа
        self.left_arrow_enabled = False # По умолчанию наконечник слева не рисуется

        '''Устанавливаем перо для рисование стрелки'''
        self.pen = QPen(self.color, self.pen_width, Qt.SolidLine)

        self.update_arrow() # Когда стрелка добавлена на сцену, вызываем её обновление

    '''Метод обновления толщины стрелки'''
    def change_width(self, width):
        self.pen_width = width              # Получаем новую толщину стрелки из панели редактирования и записываем её в параметр толщины пера
        self.pen.setWidth(self.pen_width) # Задаем новую толщину пера
        self.update()                     # Перерисовываем стрелку

    '''Метод для изменения цвета стрелки'''
    def change_color(self, color):
        self.pen.setColor(color)    # Задаем новый цвет пера, полученный из color
        self.color = color          # Перезаписываем параметр цвета
        self.update()               # Перерисовываем стрелку

    '''Метод для изменения типа линии стрелки'''
    def change_line_type(self, line_type):
        if line_type == "solid":            # Если пользователь выбрал сплошную
            self.pen.setStyle(Qt.SolidLine)
        elif line_type == "dashed":         # Если пользователь выбрал пунктирную
            self.pen.setStyle(Qt.DashLine)
        elif line_type == "dotted":         # Если пользователь выбрал точечную
            self.pen.setStyle(Qt.DotLine)
        elif line_type == "dash_dot":       # Если пользователь выбрал чередующую (точка - пунктир)
            self.pen.setStyle(Qt.DashDotLine)
        
        self.line_type = line_type # Перезаписываем параметр толщины стрелки
        self.update() # Перерисовываем стрелку

    '''Область охватывания стрелки'''
    def boundingRect(self):
        extra_margin = 90                       # Добавочная область вокруг стрелки
        rect = self.path.boundingRect()         # Получаем ограничивающий прямоугольник для пути
        return rect.adjusted(-extra_margin, -extra_margin, extra_margin, extra_margin)  # Добавляем отступ

    '''Отрисовка стрелки'''
    def paint(self, painter, option, widget=None):
        # Включаем сглаживание для улучшения качества отрисовки
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen)    # Используем ранее настроенное перо
        painter.drawPath(self.path) # Рисуем путь стрелки

        # Если нужно показать промежуточные точки
        if self.show_points:
            painter.setPen(QPen(Qt.black))                  # Устанавливаем черное перо (черный контур)
            painter.setBrush(QBrush(QColor(60, 60, 60)))    # Устанавливаем серую кисть для заполнения точек
            # Рисуем промежуточные точки, радиусом 5 пикселей каждая.
            for point in self.intermediate_points:
                painter.drawEllipse(point, 5, 5)

    '''Удаление стрелки'''
    def remove_arrow(self):
        if self.is_removed:
            return  # Если стрелка уже удалена, ничего не делаем
        
        # Удаляем стрелку из сцены
        self.scene().removeItem(self)

        # Удаляем стрелку из списков узлов
        if self.node1 and self in self.node1.arrows: # Если стрелка связана с первым узлом
            self.node1.arrows.remove(self)           # удаляем её из списка стрелок первого узла
        if self.node2 and self in self.node2.arrows: # Если стрелка связана со вторым узлом 
            self.node2.arrows.remove(self)           # удаляем её из списка стрелок второго узла
    

        # Обновляем флаг и очищаем ссылки на первый и второй элемент(node1 и node2)
        self.is_removed = True
        self.node1 = None
        self.node2 = None

    '''Обновление стрелки'''
    def update_arrow(self):
        # Если один из узлов отсутствует или стрелка не принадлежит сцене, ничего не делаем
        if not self.node1 or not self.node2 or not self.scene():
            return

        # Получаем центры ограничивающих прямоугольников для узлов
        start_center = self.node1.sceneBoundingRect().center() # Для 1-го элемента
        end_center = self.node2.sceneBoundingRect().center()   # Для 2-го элемента

        # Получаем ограничивающие прямоугольники узлов
        node1_rect = self.node1.sceneBoundingRect() # Для 1-го элемента
        node2_rect = self.node2.sceneBoundingRect() # Для 2-го элемента

        # Вычисляем точки пересечения края прямоугольника узла и линии между узлами
        start_point = self.get_edge_intersection(node1_rect, start_center, end_center) # Для 1-го элемента
        end_point = self.get_edge_intersection(node2_rect, end_center, start_center)   # Для 2-го элемента

        # Если относительные промежуточные точки ещё не заданы, вычисляем их
        if not self.relative_points:
            self.relative_points = [
                QPointF(point.x() - start_point.x(), point.y() - start_point.y())
                for point in self.intermediate_points
            ]
        
        # Вычисляем абсолютные координаты промежуточных точек относительно начальной точки
        self.intermediate_points = [
            QPointF(start_point.x() + rel_point.x(), start_point.y() + rel_point.y())
            for rel_point in self.relative_points
        ]

        # Формируем список всех точек пути (начало, промежуточные точки, конец)
        points = [start_point] + self.intermediate_points + [end_point]
        path = QPainterPath()       # Создаем путь
        path.moveTo(points[0])      # Начинаем путь с первой точки
        for point in points[1:]:    # Прорисовываем линии между всеми точками
            path.lineTo(point)      # Добавляем в путь промежуточные точки

        # Размер стрелок
        arrow_size = 15.0

        # Рисуем стрелку на правом конце (если включено)
        if self.right_arrow_enabled:
            # Вычисляем угол наклона линии между последними двумя точками
            angle = atan2(end_point.y() - points[-2].y(), end_point.x() - points[-2].x())
            # Вычисляем координаты двух точек, формирующих стрелку
            arrow_p1 = QPointF(end_point.x() - arrow_size * cos(angle - pi / 6),
                               end_point.y() - arrow_size * sin(angle - pi / 6))
            arrow_p2 = QPointF(end_point.x() - arrow_size * cos(angle + pi / 6),
                               end_point.y() - arrow_size * sin(angle + pi / 6))
            # Рисуем линии стрелки
            path.moveTo(end_point)
            path.lineTo(arrow_p1)
            path.moveTo(end_point)
            path.lineTo(arrow_p2)

        # Рисуем стрелку на левом конце (если включено)
        if self.left_arrow_enabled:
            # Вычисляем угол наклона линии между первыми двумя точками (с противоположным направлением)
            angle = atan2(points[1].y() - start_point.y(), points[1].x() - start_point.x()) + pi
            # Вычисляем координаты двух точек, формирующих стрелку
            arrow_p1 = QPointF(start_point.x() - arrow_size * cos(angle - pi / 6),
                               start_point.y() - arrow_size * sin(angle - pi / 6))
            arrow_p2 = QPointF(start_point.x() - arrow_size * cos(angle + pi / 6),
                               start_point.y() - arrow_size * sin(angle + pi / 6))
            # Рисуем линии стрелки
            path.moveTo(start_point)
            path.lineTo(arrow_p1)
            path.moveTo(start_point)
            path.lineTo(arrow_p2)

        self.path = path    # Сохраняем путь для стрелки
        self.update()       # Обновляем элемент на сцене


    '''Событие нажатия на стрелку'''
    def mousePressEvent(self, event):
        pos = event.pos() # Перед созданием точки получаем позицию курсора в момент нажатия

        # Если нажата правая кнопка мыши
        if event.button() == Qt.RightButton:
            # Удаление точки, если попали в существующую
            for i, point in enumerate(self.intermediate_points):
                if QLineF(pos, point).length() < 10:     # Если расстояние меньше 10 пикселей
                    del self.intermediate_points[i]      # Удаляем точку из списка промежуточных точек
                    del self.relative_points[i]          # Удаляем соответствующую относительную точку
                    self.update_arrow()                  # Обновляем путь стрелки и завершаем событие
                    return

            # Добавление новой точки, если клик был вне существующих точек
            if self.node1:                                              # Проверяем, что начальный узел существует
                start_point = self.node1.sceneBoundingRect().center()    # Центр начального узла
                # Вычисляем относительные координаты точки относительно начального узла
                relative_pos = QPointF(pos.x() - start_point.x(), pos.y() - start_point.y())
                self.relative_points.append(relative_pos) # Добавляем эту точку в список относительных точек
                self.intermediate_points.append(pos)      # Добавление точки в основной список точек
                self.update_arrow() # Перерисовываем стрелку
            return

        # Перетаскивание существующей точки
        for i, point in enumerate(self.intermediate_points):
            if QLineF(pos, point).length() < 10: # Если курсор рядом с существующей точкой
                self.dragged_point_index = i     # сохраняем её индекс
                return

        super().mousePressEvent(event) # Если никакая точка не перетаскивается выполняется стандартная обработка

    '''Событие перемещение стрелки(а так же её точек) по сцене'''
    def mouseMoveEvent(self, event):
        if self.dragged_point_index is not None:    # Если пользователь перетаскивает одну из промежуточных точек,
            new_pos = event.pos()                   # то получаем новое положение курсора
            # Обновляем положение перетаскиваемой точки
            self.intermediate_points[self.dragged_point_index] = new_pos
            start_point = self.node1.sceneBoundingRect().center()               # Вычесляем центр начального узла
            self.relative_points[self.dragged_point_index] = QPointF(           # и боновляем её относительные 
                new_pos.x() - start_point.x(), new_pos.y() - start_point.y()    # координаты точки
            )
            self.update_arrow() # Обновляем стрелку
        else:
            super().mouseMoveEvent(event) # Если никакая точка не перемещается выполняется стандартная обработка

    '''Событие завершения нажатия'''
    def mouseReleaseEvent(self, event):
        # Сбрасываем индекс перетаскиваемой точки, так как перетаскивание завершено
        self.dragged_point_index = None
        super().mouseReleaseEvent(event)

    '''Определение точки пересечения линии (между стартовой и конечной точками) с границей прямоугольника.'''
    def get_edge_intersection(self, rect, start, end):
        # Проверяем, есть ли пересечение
        if rect.isNull():  
            return start

        line = QLineF(start, end) # Создаём линию из начальной в конечную точку

        top_edge = QLineF(rect.topLeft(), rect.topRight())
        bottom_edge = QLineF(rect.bottomLeft(), rect.bottomRight())
        left_edge = QLineF(rect.topLeft(), rect.bottomLeft())
        right_edge = QLineF(rect.topRight(), rect.bottomRight())

        edges = [top_edge, bottom_edge, left_edge, right_edge]

        intersection_point = QPointF()
        for edge in edges:
            if line.intersect(edge, intersection_point) == QLineF.BoundedIntersection:
                return intersection_point
        return start  # Возвращаем начальную точку, если нет пересечений

    '''Для удаления стрелок со сцены которых на самом деле нет'''
    def advance(self, phase):
        if phase == 0:  # Фаза 0 - проверка состояния
            if not self.scene():  # Если стрелка не в сцене, ничего не делаем
                return
            # Если узлы больше не существуют или стрелка уже удалена, убрать её
            if not self.node1 or not self.node2 or self.is_removed:
                self.remove_arrow()

'''Класс Decision(Ромб)'''
class Decision(QGraphicsPolygonItem):
    def __init__(self, x, y, size, color=Qt.white, node1=None, node2=None):
        super().__init__()

        # Уникальный идентификатор
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1

        # Основные параметры
        self.size = size
        self.center_x = x
        self.center_y = y
        self.color = color
        self.border_color = Qt.black

        # Установка начального состояния
        self.setPolygon(self.create_diamond(self.center_x, self.center_y, self.size))
        self.setBrush(self.color)
        self.setPen(QPen(self.border_color, 2))

        # Флаги
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Состояние для изменения размера
        self.is_resizing = False
        self.resize_side = None
        self.resize_margin = 10

        # Список стрелок
        self.arrows = []

        # Узлы
        self.node1 = node1
        self.node2 = node2

    def create_diamond(self, x, y, size):
        """Создает ромб с заданным центром и размером."""
        half_size = size / 2
        return QPolygonF([
            QtCore.QPointF(x, y - half_size),  # Верхняя вершина
            QtCore.QPointF(x + half_size, y),  # Правая вершина
            QtCore.QPointF(x, y + half_size),  # Нижняя вершина
            QtCore.QPointF(x - half_size, y)   # Левая вершина
        ])

    """Устанавливает цвет ромба."""
    def set_color(self, color):
        self.color = color
        self.setBrush(self.color)
        self.update()

    def hoverMoveEvent(self, event):
        """Обрабатывает наведение мыши для изменения курсора и определения стороны изменения размера."""
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем ближайшую сторону для изменения размера
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.resize_side = None

        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Обрабатывает нажатие мыши."""
        self.is_resizing = self.resize_side is not None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Обрабатывает перемещение мыши, обновляет размеры или перемещение объекта."""
        if self.is_resizing:
            self._resize(event)
        else:
            super().mouseMoveEvent(event)

        # Обновляем стрелки при движении объекта
        for arrow in self.arrows:
            arrow.update_arrow()

    def mouseReleaseEvent(self, event):
        """Обрабатывает завершение нажатия мыши."""
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def _resize(self, event):
        """Изменяет размер ромба в зависимости от положения курсора."""
        delta_x = abs(event.pos().x() - self.center_x)
        delta_y = abs(event.pos().y() - self.center_y)
        new_size = max(10, max(delta_x, delta_y) * 2)  # Минимальный размер 10
        
        self.size = new_size
        self.setPolygon(self.create_diamond(self.center_x, self.center_y, self.size))

    def paint(self, painter, option, widget=None):
        """Включает сглаживание при отрисовке."""
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        """Обновляет стрелки при изменении позиции объекта."""
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:
                    arrow.update_arrow()
        return super().itemChange(change, value)

    """Добавление стрелки к объекту."""
    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)
            arrow.update_arrow()

    """Создание копии объекта."""
    def clone(self):
        clone_item = Decision(self.center_x, self.center_y, self.size, self.color)
        clone_item.setPolygon(self.polygon())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        return clone_item

'''Класс StartEvent(Круг)'''
class StartEvent(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, radius: float, color=Qt.black):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)

        # Уникальный идентификатор объекта
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1

        # Основные параметры
        self.x_center = x
        self.y_center = y
        self.radius = radius
        self.color = color

        # Настройка внешнего вида
        self.setBrush(self.color)
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Флаги и параметры изменения размера
        self.is_resizing = False
        self.resize_side = None
        self.resize_margin = 10  # Размер области для изменения

        # Привязанные стрелки
        self.arrows: list[Arrow] = []

    def add_arrow(self, arrow: 'Arrow'):
        """Добавляет стрелку к узлу."""
        if arrow not in self.arrows:
            self.arrows.append(arrow)

    def remove_all_arrows(self):
        """Удаляет все стрелки, привязанные к узлу."""
        for arrow in list(self.arrows):  # Создаем копию списка для безопасного удаления
            if arrow.scene():
                arrow.remove_arrow()
        self.arrows.clear()

    def clone(self) -> 'StartEvent':
        """Создает копию текущего объекта."""
        clone_item = StartEvent(self.x_center, self.y_center, self.radius, self.color)
        clone_item.setRect(self.rect())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        return clone_item

    def set_radius(self, new_radius: float):
        """Устанавливает новый радиус и обновляет стрелки."""
        self.radius = new_radius
        self.setRect(self.x() - new_radius, self.y() - new_radius, new_radius * 2, new_radius * 2)
        for arrow in self.arrows:
            arrow.update_arrow()

    def hoverMoveEvent(self, event):
        """Обрабатывает наведение мыши для изменения размера."""
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определение стороны для изменения размера
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.resize_side = None

        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Определяет начало изменения размера или перемещения."""
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Обрабатывает перемещение объекта или изменение его размера."""
        if self.is_resizing:
            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

            if self.resize_side in ['right', 'bottom']:
                # Пропорциональное изменение размера от правого или нижнего края
                delta = max(event.pos().x() - x, event.pos().y() - y)
                new_size = max(10, delta)  # Минимальный размер
                self.setRect(x, y, new_size, new_size)
            elif self.resize_side in ['left', 'top']:
                # Пропорциональное изменение размера от левого или верхнего края
                delta = max(x + w - event.pos().x(), y + h - event.pos().y())
                new_size = max(10, delta)
                new_x = x + w - new_size
                new_y = y + h - new_size
                self.setRect(new_x, new_y, new_size, new_size)

            self.radius = self.rect().width() / 2
        else:
            super().mouseMoveEvent(event)

        # Обновляем стрелки после изменения
        for arrow in self.arrows:
            arrow.update_arrow()

    def mouseReleaseEvent(self, event):
        """Сбрасывает флаг изменения размера."""
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Обрабатывает изменения объекта, включая перемещение."""
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        """Отрисовывает объект с включенным сглаживанием."""
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

'''Дочерний элемент(внтуренний круг) EndEvent'''
class InnerCircle(QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBrush(QtGui.QBrush(QColor(0, 0, 0))) # Задаем черную кисть

    def paint(self, painter, option, widget):
        # Включаем сглаживание
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)
            
'''Класс EndEvent (Круг с внутренним кругом)'''
class EndEvent(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, inner_radius_ratio=0.5, color=Qt.white, node1=None, node2=None):
        super().__init__(x - radius, y - radius, 2 * radius, 2 * radius)
        
        # Глобальный индефикатор
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1

        # Основные параметры
        self.x_center = x
        self.y_center = y
        self.radius = radius
        self.inner_radius_ratio = inner_radius_ratio
        self.color = color

        # Настройка отображения объекта
        self.setBrush(color)
        self.setPen(QPen(QColor(0, 0, 0), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Внутренние параметры
        self.is_resizing = False
        self.resize_side = None
        self.resize_margin = 10
        self.arrows = []  # Список связанных стрелок

        # Создание внутреннего круга
        self.inner_circle = InnerCircle(self)
        self.update_inner_circle()

    def clone(self):
        """Клонирует объект с сохранением всех параметров."""
        clone_item = EndEvent(self.x_center, self.y_center, self.radius, self.inner_radius_ratio)
        clone_item.setRect(self.rect())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        clone_item.update_inner_circle()
        return clone_item

    def set_radius(self, new_radius):
        """Устанавливает новый радиус внешнего круга и обновляет связанные элементы."""
        self.radius = new_radius
        self.setRect(self.x() - new_radius, self.y() - new_radius, new_radius * 2, new_radius * 2)
        self.update_inner_circle()
        self.update_arrows()

    def update_inner_circle(self):
        """Обновляет положение и размер внутреннего круга."""
        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()
        inner_radius = min(rect.width(), rect.height()) * self.inner_radius_ratio / 2
        self.inner_circle.setRect(cx - inner_radius, cy - inner_radius, inner_radius * 2, inner_radius * 2)

    def hoverMoveEvent(self, event):
        """Обрабатывает наведение мыши для изменения курсора вблизи границ."""
        cursor, resize_side = self._determine_resize_cursor(event.pos())
        self.setCursor(cursor)
        self.resize_side = resize_side
        super().hoverMoveEvent(event)

    def _determine_resize_cursor(self, pos):
        """Определяет тип курсора и сторону изменения размера."""
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        if abs(pos.x() - x) <= self.resize_margin:
            return QCursor(Qt.SizeHorCursor), 'left'
        elif abs(pos.x() - (x + w)) <= self.resize_margin:
            return QCursor(Qt.SizeHorCursor), 'right'
        elif abs(pos.y() - y) <= self.resize_margin:
            return QCursor(Qt.SizeVerCursor), 'top'
        elif abs(pos.y() - (y + h)) <= self.resize_margin:
            return QCursor(Qt.SizeVerCursor), 'bottom'
        return QCursor(Qt.ArrowCursor), None

    def mousePressEvent(self, event):
        """Обрабатывает нажатие мыши."""
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Обрабатывает перемещение объекта или изменение его размера."""
        if self.is_resizing:
            self._resize(event.pos())
        else:
            super().mouseMoveEvent(event)
        self.update_arrows()

    def _resize(self, pos):
        """Изменяет размер объекта в зависимости от направления."""
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if self.resize_side in ['right', 'bottom']:
            delta = max(pos.x() - x, pos.y() - y)
        elif self.resize_side in ['left', 'top']:
            delta = max(x + w - pos.x(), y + h - pos.y())
            x, y = x + w - delta, y + h - delta
        else:
            return

        new_size = max(10, delta)  # Минимальный размер
        self.setRect(x, y, new_size, new_size)
        self.update_inner_circle()

    def mouseReleaseEvent(self, event):
        """Сбрасывает флаг изменения размера."""
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        """Отрисовка объекта с включенным сглаживанием."""
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        """Обрабатывает изменения позиции объекта."""
        if change == QGraphicsItem.ItemPositionChange:
            self.update_arrows()
        return super().itemChange(change, value)

    def update_arrows(self):
        """Обновляет все связанные стрелки."""
        for arrow in self.arrows:
            arrow.update_arrow()

    def add_arrow(self, arrow):
        """Добавляет стрелку к списку связанных стрелок."""
        if arrow not in self.arrows:
            self.arrows.append(arrow)

'''Дочерний элемент(текст) AcriveState, SignalSending и SignalReceipt'''
class Text_into_object(QtWidgets.QGraphicsTextItem):
    def __init__(self, max_length, parent=None):
        super().__init__(parent)
        self.unique_id = None
        self.max_length = max_length
        self.setTextInteractionFlags(Qt.NoTextInteraction)  # Отключаем редактирование текста по умолчанию

    def keyPressEvent(self, event):
        current_text = self.toPlainText()

        # Если текст слишком длинный, блокируем ввод, за исключением клавиш Backspace, Delete, Left, Right
        if len(current_text) >= self.max_length and event.key() not in (
            Qt.Key_Backspace,
            Qt.Key_Delete,
            Qt.Key_Left,
            Qt.Key_Right,
        ):
            event.ignore()  # Игнорируем событие
            return

        super().keyPressEvent(event)  # Делаем стандартную обработку, если условия не выполнены

    def focusOutEvent(self, event):
        # При потере фокуса выключаем редактирование
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)  # Стандартная обработка фокуса

    def update_wrapped_text(self, max_width):
        # Обновление текста с автоматическим переносом
        font_metrics = QtGui.QFontMetrics(self.font())  # Получаем метрики шрифта
        current_text = self.toPlainText()
        words = current_text.split()  # Разбиваем текст на слова
        current_line = ""
        wrapped_text = ""

        for word in words:
            # Пробуем добавить слово в текущую строку
            test_line = f"{current_line} {word}".strip()
            if font_metrics.width(test_line) <= max_width:
                current_line = test_line
            else:
                wrapped_text += f"{current_line}\n"  # Добавляем строку и переносим на новую
                current_line = word  # Начинаем новую строку с текущего слова

        wrapped_text += current_line  # Добавляем оставшуюся часть текста
        self.setPlainText(wrapped_text)  # Обновляем текст

    def mousePressEvent(self, event):
        # Перехватываем нажатие правой кнопки мыши, чтобы предотвратить обычную обработку
        if event.button() == Qt.RightButton:
            event.ignore()  # Игнорируем правый клик
            return
        super().mousePressEvent(event)  # Стандартная обработка для других кликов

    def contextMenuEvent(self, event):
        # Блокируем контекстное меню
        event.ignore()  # Игнорируем вызов контекстного меню

    def eventFilter(self, obj, event):
        # Фильтруем события для блокировки правого клика мыши
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            return True  # Блокируем дальнейшую обработку правого клика
        return super().eventFilter(obj, event)  # Стандартная обработка остальных событий

'''Класс ActiveState'''
class ActiveState(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, width, height, radius, color=QtCore.Qt.white, node1=None, node2=None):
        super().__init__(x, y, width, height)
        # Объявление глобальной переменной
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1

        # Центры объетка, ширина, высота, радиус углов, цвет
        self.x_center = x
        self.y_center = y
        self.width = width
        self.height = height
        self.radius = radius  # Радиус закругления
        self.color = color

        # Установка цвета, пера, флагов и тд.
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
        self.update_text_wrap()
        self.update_text_position()

    '''Клонирование объекта'''
    def clone(self):
        cloned_item = ActiveState(self.x_center, self.y_center, self.width, self.height, self.radius)
        cloned_item.setRect(self.rect())
        cloned_item.setBrush(self.brush())
        cloned_item.setPen(self.pen())
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())
        return cloned_item

    '''Переброс строки по пробелам при изменении размера объекта'''
    def update_text_wrap(self):
        rect = self.rect()
        text_width = rect.width() - 10  # Отступы по 5px с каждой стороны
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

    '''Центрирование текста при измененни размера'''
    def update_text_position(self):
        rect = self.rect()
        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()
        center_x = rect.x() + rect.width() / 2
        center_y = rect.y() + rect.height() / 2

        # Устанавливаем текст по центру
        self.text_item.setPos(center_x - text_width / 2, center_y - text_height / 2)

    '''Отрисовка объекта'''
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

    '''Событие при наведении на объект'''
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

    '''Включение редактирование текста при двойном нажатии на элемент'''
    def mouseDoubleClickEvent(self, event):
        if self.text_item.textInteractionFlags() == QtCore.Qt.NoTextInteraction:
            self.text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            self.text_item.setFocus(QtCore.Qt.MouseFocusReason)
        else:
            self.text_item.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        super().mouseDoubleClickEvent(event)

    '''Событие передвижения объекта'''
    def mouseMoveEvent(self, event):
        # Обновляем стрелки, привязанные к этому обекту
        for arrow in self.arrows:
            arrow.update_arrow()
        # При изменении размера объекта
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

            # Обновляем позицию текста
            self.update_text_position()
            self.update_text_wrap()
        else:
            super().mouseMoveEvent(event)

    '''При завершении правого клика'''
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
    
    '''Добавление стрелки'''
    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

'''Класс SignalSending (Прямоугольный пятиугольник)'''
class SignalSending(QGraphicsPolygonItem):
    # Инициализация объекта
    def __init__(self, x, y, width, height, trans, color=Qt.white, node1=None, node2=None):
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8  # Уникальный ID объекта
        GLOBAL_ID += 1
        super().__init__()
        
        # Инициализация параметров
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.color = color
        self.trans = trans

        # Создание пентагона, установка внешнего вида
        self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.width, self.height))
        self.setBrush(color)
        self.setPen(QPen(QColor(0, 0, 0), 2))
        
        # Установка флагов для перемещения и взаимодействия
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Инициализация флагов и состояний для изменения размера
        self.is_resizing = False
        self.resize_side = None
        self.resize_margin = 10  # Чувствительная область для изменения размера
        self.current_reflection = "Справа"  # Начальное отражение объекта

        # Инициализация стрелок и текста
        self.arrows = []
        self.text_item = Text_into_object(15, self)
        self.text_item.setPlainText("Signal Sending")
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        
        # Обновление текста
        self.update_text_wrap()
        self.update_text_position()

    # Клонирование объекта
    def clone(self):
        cloned_item = SignalSending(self.center_x, self.center_y, self.width, self.height, self.current_reflection)
        cloned_item.setPolygon(self.polygon())  # Копируем форму
        cloned_item.setBrush(self.brush())  # Копируем цвет
        cloned_item.setPen(self.pen())  # Копируем обводку
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())  # Копируем текст
        cloned_item.reflect(self.current_reflection)  # Копируем отражение

        return cloned_item

    # Обновление обертки текста
    def update_text_wrap(self):
        rect = self.boundingRect()
        text_width = rect.width() - 10
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

    # Создание пентагона на основе координат и размеров
    def create_pentagon(self, x, y, width, height):
        points = [
            QtCore.QPointF(x - width / 2, y),          # Середина слева
            QtCore.QPointF(x + width / 2, y),          # Середина справа
            QtCore.QPointF(x + width*0.7, y - height / 2),  # Середина внизу
            QtCore.QPointF(x + width / 2, y - height),   # Нижний левый угол
            QtCore.QPointF(x - width / 2, y - height)    # Середина слева
        ]

        polygon = QPolygonF(points)
        return polygon

    # Обновление позиции текста относительно объекта
    def update_text_position(self):
        center_x = self.center_x
        center_y = self.center_y - self.height / 2 

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

    # Отражение объекта в заданном направлении
    def reflect(self, direction):
        self.current_reflection = direction

        # Получаем текущий центр объекта в сцене
        original_scene_center = self.sceneBoundingRect().center()

        transform = QTransform()
        if direction == "Слева":  # Отразить по вертикальной оси
            transform.scale(-1, 1)
        elif direction == "Справа":  # Отразить по горизонтальной оси
            transform.scale(1, -1)
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

    # Обработчик перемещения мыши над объектом (для изменения размера)
    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    # Обработчик нажатия мыши (для начала изменения размера)
    def mousePressEvent(self, event):
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    # Обработчик перемещения мыши (для изменения размера)
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

    # Обработчик отпускания кнопки мыши (завершение изменения размера)
    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # Обработчик двойного клика (для редактирования текста)
    def mouseDoubleClickEvent(self, event):
        print("Произошел двойной клик по элементу")
        if self.text_item.textInteractionFlags() == Qt.NoTextInteraction:
            self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.text_item.setFocus(Qt.MouseFocusReason)
        else:
            self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        super().mouseDoubleClickEvent(event)

    # Сглаживание отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

    # Обработка изменений позиции объекта
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)

    # Добавление стрелки к объекту
    def add_arrow(self, arrow):
        self.arrows.append(arrow)

'''Класс SignalSending (Прямоугольный пятиугольник с вогнутым углом)'''
class SignalReceipt(QGraphicsPolygonItem):
    def __init__(self, x, y, width, height, trans, color=Qt.white, node1=None, node2=None):
        super().__init__()
        # Установка уникального индефикатора
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1
        
        # Параметры объекта
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.color = color
        self.trans = trans

        # Создаем пентагон
        self.setPolygon(self.create_pentagon(self.center_x, self.center_y, self.width, self.height))
        self.setBrush(color)
        self.setPen(QPen(QColor(0, 0, 0), 2))
        
        # Устанавливаем флаги для движения и выбора объекта
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        # Инициализация флагов и переменных для изменения размера
        self.is_resizing = False  # Флаг изменения размера
        self.resize_side = None   # Сторона изменения размера
        self.resize_margin = 10   # Чувствительная область для изменения размера
        self.current_reflection = "None"  # Направление отражения
        self.current_reflection = "Слева" # Начальное направление отражения

        # Инициализация списка стрелок
        self.arrows = []

        # Инициализация текстового объекта
        self.text_item = Text_into_object(15, self)
        self.text_item.setPlainText("Signal receipt")
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.update_text_wrap()
        self.update_text_position()

    # Клонирование объекта
    def clone(self):
        cloned_item = SignalReceipt(self.center_x, self.center_y, self.width, self.height, self.current_reflection)
        cloned_item.setPolygon(self.polygon())
        cloned_item.setBrush(self.brush())
        cloned_item.setPen(self.pen())
        
        cloned_item.text_item.setPlainText(self.text_item.toPlainText())
        cloned_item.reflect(self.current_reflection)

        return cloned_item

    # Обновление обертки текста при изменении размера
    def update_text_wrap(self):
        rect = self.boundingRect()
        text_width = rect.width() - 10
        if text_width > 0:
            self.text_item.update_wrapped_text(text_width)

    # Создание пентагона по заданным параметрам
    def create_pentagon(self, x, y, width, height):
        points = [
            QtCore.QPointF(x + width * (-0.325), y - height / 2),  # Угол слева
            QtCore.QPointF(x - width / 2, y),          # Первая точка
            QtCore.QPointF(x + width / 2, y),          # Точка напротив неё
            QtCore.QPointF(x + width / 2, y - height),   # Первая нижняя точка
            QtCore.QPointF(x - width / 2, y - height)    # Точка напротив неё
        ]

        polygon = QPolygonF(points)

        return polygon

    # Обновление позиции текста на основе отражения
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

    # Отражение объекта по оси
    def reflect(self, direction):
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
        self.update_text_position()

    # Обработчик движения мыши (перемещение и изменение размера)
    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resize_side = 'bottom'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.resize_side = None
        super().hoverMoveEvent(event)

    # Обработчик нажатия кнопки мыши (начало изменения размера)
    def mousePressEvent(self, event):
        self.is_resizing = bool(self.resize_side)
        super().mousePressEvent(event)

    # Обработчик движения мыши (изменение размера)
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

    # Обработчик отпускания кнопки мыши (завершение изменения размера)
    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # Обработчик двойного клика (редактирование текста)
    def mouseDoubleClickEvent(self, event):
        print("Произошел двойной клик по элементу")
        if self.text_item.textInteractionFlags() == Qt.NoTextInteraction:
            self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
            self.text_item.setFocus(Qt.MouseFocusReason)
        else:
            self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        super().mouseDoubleClickEvent(event)

    # Сглаживание отрисовки объекта
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

    # Обработчик изменения позиции объекта (обновление стрелок)
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Если изменяется позиция, обновляем стрелки
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции
        return super().itemChange(change, value)  # Обработка остальных изменений

    # Добавление стрелки
    def add_arrow(self, arrow):
        self.arrows.append(arrow)

'''Класс Splitter_Merge(Сжатый прямоугольник)'''
class Splitter_Merge(QGraphicsPolygonItem):
    def __init__(self, x, y, width, height, rot, color=Qt.black, node1=None, node2=None):
        super().__init__()

        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8  # Уникальный идентификатор объекта
        GLOBAL_ID += 1

        self.width = width  # Ширина объекта
        self.height = height  # Высота объекта
        self.center_x = x  # Координата X центра
        self.center_y = y  # Координата Y центра
        self.rot = rot  # Угол поворота объекта
        self.color = color  # Цвет объекта

        # Устанавливаем начальную форму объекта
        self.setPolygon(self.create_SM(self.center_x, self.center_y, self.width, self.height))

        # Настройка кисти и пера для рисования
        self.setBrush(color)
        self.setPen(QPen(QColor(0, 0, 0), 2))

        # Устанавливаем флаги для перемещения и выделения объекта
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        # Включаем поддержку событий наведения мыши
        self.setAcceptHoverEvents(True)

        # Центрирование объекта при смене ориентации
        rect = self.boundingRect()
        self.setTransformOriginPoint(self.center_x, self.center_y)

        # Переменные для изменения размера
        self.is_resizing = False  # Флаг, указывающий, идет ли изменение размера
        self.resize_side = None  # Сторона, с которой идет изменение размера
        self.resize_margin = 10  # Чувствительная область для изменения размера

        self.arrows = []  # Список стрелок, привязанных к объекту

    # Метод для клонирования объекта
    def clone(self):
        clone_item = Splitter_Merge(self.center_x, self.center_y, self.width, self.height, self.rot)
        clone_item.setPolygon(self.polygon())
        clone_item.setBrush(self.brush())
        clone_item.setPen(self.pen())
        return clone_item

    # Создает форму для объекта (прямоугольный пятиугольник)
    def create_SM(self, x, y, width, height):
        points = [
            QtCore.QPointF(x - width / 2, y),  # Первая точка
            QtCore.QPointF(x + width / 2, y),  # Точка напротив неё
            QtCore.QPointF(x + width / 2, y - height / 2),  # Первая нижняя точка
            QtCore.QPointF(x - width / 2, y - height / 2)  # Точка напротив неё
        ]

        sm = QPolygonF(points)
        return sm

    # Обновление размеров и ориентации объекта
    def update_size_and_orientation(self, width, height, rotation):
        self.setPolygon(self.create_SM(self.center_x, self.center_y, width, height))
        self.setRotation(rotation)
        self.rot = rotation
        self.update()

    # Обработчик событий перемещения мыши (для изменения размера)
    def hoverMoveEvent(self, event):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        # Определяем, в какую сторону пользователь пытается изменить размер
        if abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resize_side = 'right'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.resize_side = None

        super().hoverMoveEvent(event)

    # Обработчик нажатия мыши (для начала изменения размера)
    def mousePressEvent(self, event):
        self.is_resizing = bool(self.resize_side)  # Проверка, начали ли изменять размер
        super().mousePressEvent(event)

    # Обработчик перемещения мыши (для изменения размера)
    def mouseMoveEvent(self, event):
        # Обновляем все привязанные стрелки
        for arrow in self.arrows:
            arrow.update_arrow()

        if self.is_resizing:
            delta_x = abs(event.pos().x() - self.center_x)
            delta_y = abs(event.pos().y() - self.center_y)

            # Изменение ширины или высоты в зависимости от выбранной стороны
            if self.resize_side in ['left', 'right']:
                new_width = max(10, delta_x * 2)
                self.width = new_width
            if self.resize_side in ['top', 'bottom']:
                new_height = max(10, delta_y * 2)
                self.height = new_height

            # Обновляем форму объекта
            new_polygon = self.create_SM(self.center_x, self.center_y, self.width, self.height)
            self.setPolygon(new_polygon)
        else:
            super().mouseMoveEvent(event)

    # Обработчик отпускания мыши (завершаем изменение размера)
    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        super().mouseReleaseEvent(event)

    # Сглаживание отрисовки объекта (включение антиалиасинга)
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)

    # Обработчик изменения позиции объекта
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # Обновляем привязанные стрелки при изменении позиции
            for arrow in self.arrows:
                if arrow.node1 and arrow.node2:  # Проверка, что стрелка всё ещё привязана к узлам
                    arrow.update_arrow()  # Обновляем стрелку, чтобы она следовала за объектом
            return value  # Возвращаем новое значение позиции

        return super().itemChange(change, value)  # Обработка остальных изменений

    # Добавление стрелки к объекту
    def add_arrow(self, arrow):
        self.arrows.append(arrow)

'''Класс картинки'''
class ImageItem(QtWidgets.QGraphicsPixmapItem):
     
    def __init__(self, pixmap, x, y):
        super().__init__(pixmap)
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1
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

    def mousePressEvent(self, event):
        if self.cursor().shape() in [Qt.SizeHorCursor, Qt.SizeVerCursor]:
            self.is_resizing = True
        else:
            self.is_resizing = False
        super().mousePressEvent(event)

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
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)


class Text_Edit(Text_into_object):
     
    def __init__(self, x, y, width, height, text="Текст", max_length=250, parent=None):
        super().__init__(max_length, parent)
        global GLOBAL_ID
        self.unique_id = GLOBAL_ID - 8
        GLOBAL_ID += 1
        self.setPlainText(text)
        self.max_length = max_length

        self.x_center = x
        self.y_center = y
        self.arrows = []

        self.setPos(self.x_center, self.y_center)
        self.setFont(QtGui.QFont("Arial", 12))
        self.setDefaultTextColor(QColor(0, 0, 0))

        self.setTextInteractionFlags(Qt.TextEditorInteraction)
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
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.MouseFocusReason)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)

    def hoverMoveEvent(self, event):
        rect = self.boundingRect() 
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))  # Верхний левый угол
            self.resize_side = 'top_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))  # Верхний правый угол
            self.resize_side = 'top_right'
        elif abs(event.pos().x() - x) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))  # Нижний левый угол
            self.resize_side = 'bottom_left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin and abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))  # Нижний правый угол
            self.resize_side = 'bottom_right'
        elif abs(event.pos().x() - x) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))  # Левая сторона
            self.resize_side = 'left'
        elif abs(event.pos().x() - (x + w)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeHorCursor))  # Правая сторона
            self.resize_side = 'right'
        elif abs(event.pos().y() - y) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))  # Верхняя сторона
            self.resize_side = 'top'
        elif abs(event.pos().y() - (y + h)) <= self.resize_margin:
            self.setCursor(QCursor(Qt.SizeVerCursor))  # Нижняя сторона
            self.resize_side = 'bottom'
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
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

    '''Добавление стрелки к элементу'''
    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)    