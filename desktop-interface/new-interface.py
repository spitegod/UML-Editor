import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QFileDialog,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStatusBar, QLineEdit, QSizeGrip
)
from PyQt5.QtCore import Qt, QMimeData, QPoint, QSize
from PyQt5.QtGui import QDrag, QPixmap, QIcon, QColor, QPainter


class DraggableButton(QPushButton):
    def __init__(self, element_type, icon_pixmap, parent):
        super().__init__(parent)
        self.element_type = element_type
        self.setIcon(QIcon(icon_pixmap))
        self.setIconSize(QSize(50, 50))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.element_type)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)


class UMLItem(QWidget):
    def __init__(self, element_type, pixmap, parent=None):
        super().__init__(parent)
        self.element_type = element_type
        self.pixmap = pixmap
        self.setMinimumSize(50, 50)
        self.setFixedSize(60, 60)
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # Используем QSizeGrip для изменения размеров
        self.size_grip = QSizeGrip(self)
        self.size_grip.setVisible(True)

        # Устанавливаем прозрачный фон и рамку
        self.setStyleSheet("background: transparent; border: 1px solid gray;")

        # Переменная для хранения смещения при перетаскивании
        self.offset = QPoint()

    def resizeEvent(self, event):
        # Обновляем размеры QLabel и позицию QSizeGrip
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.size_grip.move(self.width() - self.size_grip.width(), self.height() - self.size_grip.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Запоминаем начальную позицию мыши для перемещения
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # Перемещаем элемент по рабочей области
            self.move(self.mapToParent(event.pos() - self.offset))

    def get_data(self):
        # Возвращаем данные элемента для сохранения
        return {
            "element_type": self.element_type,
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height()
        }


class DropArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #404040; border-radius: 5px;")
        self.elements = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        element_type = event.mimeData().text()
        pixmap = create_icon(element_type)
        uml_item = UMLItem(element_type, pixmap, self)
        drop_pos = event.pos()
        uml_item.move(drop_pos - QPoint(pixmap.width() // 2, pixmap.height() // 2))
        uml_item.show()
        self.elements.append(uml_item)
        event.acceptProposedAction()

    def get_elements_data(self):
        return [element.get_data() for element in self.elements]

    def clear_elements(self):
        for element in self.elements:
            element.close()
        self.elements.clear()

    def load_elements(self, elements_data):
        self.clear_elements()
        for data in elements_data:
            element_type = data["element_type"]
            pixmap = create_icon(element_type)
            uml_item = UMLItem(element_type, pixmap, self)
            uml_item.setGeometry(data["x"], data["y"], data["width"], data["height"])
            uml_item.show()
            self.elements.append(uml_item)


def create_icon(element_type):
    pixmap = QPixmap(60, 60)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    if element_type == "Decision Node":
        painter.setBrush(QColor("lightgray"))
        painter.drawPolygon([
            QPoint(30, 5), QPoint(55, 30), QPoint(30, 55), QPoint(5, 30)
        ])
    elif element_type == "Activity State":
        painter.setBrush(QColor("lightgray"))
        painter.drawRoundedRect(10, 10, 40, 40, 10, 10)
    elif element_type == "Initial Node":
        painter.setBrush(Qt.black)
        painter.drawEllipse(10, 10, 40, 40)
    elif element_type == "Final Node":
        painter.setBrush(Qt.black)
        painter.drawEllipse(10, 10, 40, 40)
        painter.setBrush(Qt.white)
        painter.drawEllipse(20, 20, 20, 20)
    elif element_type == "Fork/Join Node":
        painter.setBrush(Qt.black)
        painter.drawRect(10, 25, 40, 10)
    elif element_type == "Object Node":
        painter.setBrush(QColor("lightgray"))
        painter.drawRect(10, 10, 40, 40)
    elif element_type == "Receive Signal Action":
        painter.setBrush(QColor("lightgray"))
        painter.drawPolygon([
            QPoint(45, 30), QPoint(15, 10), QPoint(15, 50)
        ])
    elif element_type == "Send Signal Action":
        painter.setBrush(QColor("lightgray"))
        painter.drawPolygon([
            QPoint(15, 30), QPoint(45, 10), QPoint(45, 50)
        ])
    elif element_type == "Transition":
        painter.setPen(Qt.black)
        painter.drawLine(10, 30, 50, 30)
        painter.drawPolygon([
            QPoint(50, 30), QPoint(40, 25), QPoint(40, 35)
        ])

    painter.end()
    return pixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UML Activity Diagram Editor")
        self.setGeometry(100, 100, 800, 600)

        menu_bar = QMenuBar(self)
        file_menu = QMenu("Файл", self)
        file_menu.addAction("Сохранить", self.save_diagram)
        file_menu.addAction("Загрузить", self.load_diagram)
        menu_bar.addMenu(file_menu)
        self.setMenuBar(menu_bar)

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        toolbar_widget = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_widget)

        elements = [
            "Decision Node", "Activity State", "Initial Node", "Final Node",
            "Fork/Join Node", "Object Node", "Receive Signal Action",
            "Send Signal Action", "Transition"
        ]

        for element in elements:
            icon_pixmap = create_icon(element)
            button = DraggableButton(element, icon_pixmap, self)
            toolbar_layout.addWidget(button)

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar_widget)

        self.drop_area = DropArea()
        main_layout.addWidget(self.drop_area, 1)

        self.setCentralWidget(central_widget)

        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

    def save_diagram(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить диаграмму", "", "CHEP Files (*.chep)")
        if file_path:
            data = self.drop_area.get_elements_data()
            with open(file_path, 'w') as file:
                json.dump(data, file)

    def load_diagram(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить диаграмму", "", "CHEP Files (*.chep)")
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.drop_area.load_elements(data)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
