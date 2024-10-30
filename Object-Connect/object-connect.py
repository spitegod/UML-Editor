import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, \
    QGraphicsItem, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QPainter
from PyQt5.QtCore import Qt, QPointF
from math import sin, cos, pi


class DiagramEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagram Editor")
        self.setGeometry(100, 100, 800, 600)

        # Создаем сцену и представление
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)  # Исправление здесь

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
        self.selected_node = None

    def add_node(self):
        # Создаем узел в виде окружности
        node = QGraphicsEllipseItem(-15, -15, 30, 30)
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

            # Координаты начала и конца линии
            start_pos = node1.scenePos()
            end_pos = node2.scenePos()

            # Создаем линию со стрелкой
            line = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
            pen = QPen(Qt.black, 2)
            line.setPen(pen)
            self.scene.addItem(line)

            # Добавляем стрелку к линии
            arrow_size = 10.0
            angle = line.line().angle() * pi / 180.0
            dx, dy = arrow_size * -1, arrow_size / 2

            # Позиция стрелки
            arrow_p1 = QPointF(end_pos.x() + dx * cos(angle) - dy * sin(angle),
                               end_pos.y() + dx * sin(angle) + dy * cos(angle))
            arrow_p2 = QPointF(end_pos.x() + dx * cos(angle) + dy * sin(angle),
                               end_pos.y() + dx * sin(angle) - dy * cos(angle))

            path = QPainterPath()
            path.moveTo(end_pos)
            path.lineTo(arrow_p1)
            path.lineTo(arrow_p2)
            path.lineTo(end_pos)
            arrow = self.scene.addPath(path, pen, QBrush(Qt.black))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = DiagramEditor()
    editor.show()
    sys.exit(app.exec_())

