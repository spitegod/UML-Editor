import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsItem, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QPainter
from PyQt5.QtCore import Qt, QPointF
from math import cos, sin, pi, atan2, sqrt


class DiagramEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagram Editor")
        self.setGeometry(100, 100, 800, 600)

        # Создаем сцену и представление
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(Qt.white))  # Устанавливаем белый фон
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        # Основной виджет и макет
        layout = QVBoxLayout()
        layout.addWidget(self.view)

        # Кнопки добавления узлов и соединений
        self.addNodeButton = QPushButton("Add Node")
        self.addNodeButton.clicked.connect(self.add_node)
        layout.addWidget(self.addNodeButton)

        self.addEdgeButton = QPushButton("Add Edge")
        self.addEdgeButton.clicked.connect(self.add_edge)
        layout.addWidget(self.addEdgeButton)

        # Основной виджет
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Список узлов для соединения стрелками
        self.nodes = []

    def add_node(self):
        # Создаем узел в виде окружности
        node = QGraphicsEllipseItem(-15, -15, 30, 30)  # Радиус узла = 15
        node.setBrush(QBrush(Qt.yellow))
        node.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(node)

        # Сохраняем узел в список
        self.nodes.append(node)
        node.setPos(len(self.nodes) * 50, 50)  # Располагаем узлы с отступами

    def add_edge(self):
        # Соединяем два выбранных узла стрелкой
        selected_nodes = [node for node in self.nodes if node.isSelected()]
        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes

            # Центр каждого узла
            start_center = node1.sceneBoundingRect().center() + node1.scenePos()
            end_center = node2.sceneBoundingRect().center() + node2.scenePos()

            # Вычисляем направление и длину
            dx = end_center.x() - start_center.x()
            dy = end_center.y() - start_center.y()
            dist = sqrt(dx * dx + dy * dy)

            # Смещение на границу узла (радиус 15)
            radius = 15
            start_pos = QPointF(start_center.x() + radius * dx / dist,
                                start_center.y() + radius * dy / dist)
            end_pos = QPointF(end_center.x() - radius * dx / dist,
                              end_center.y() - radius * dy / dist)

            # Создаем линию со стрелкой
            line = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
            pen = QPen(Qt.darkGreen, 3)  # Цвет более темный для контраста и толще линия
            line.setPen(pen)
            self.scene.addItem(line)

            # Добавляем стрелку к линии
            arrow_size = 15.0  # Увеличиваем размер стрелки
            angle = atan2(dy, dx)

            # Координаты вершин стрелки
            arrow_p1 = QPointF(end_pos.x() - arrow_size * cos(angle - pi / 6),
                               end_pos.y() - arrow_size * sin(angle - pi / 6))
            arrow_p2 = QPointF(end_pos.x() - arrow_size * cos(angle + pi / 6),
                               end_pos.y() - arrow_size * sin(angle + pi / 6))

            path = QPainterPath()
            path.moveTo(end_pos)
            path.lineTo(arrow_p1)
            path.lineTo(arrow_p2)
            path.lineTo(end_pos)

            # Создаем темно-зеленую стрелку для лучшей видимости
            arrow = self.scene.addPath(path, pen, QBrush(Qt.darkGreen))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = DiagramEditor()
    editor.show()
    sys.exit(app.exec_())