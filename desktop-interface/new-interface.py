import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStatusBar, QLineEdit
)
from PyQt5.QtCore import Qt, QMimeData, QPoint, QSize
from PyQt5.QtGui import QDrag, QPixmap, QIcon, QColor, QPainter


class DraggableButton(QPushButton):
    def __init__(self, icon_pixmap, parent):
        super().__init__(parent)
        icon = QIcon(icon_pixmap)  # Создаем QIcon из QPixmap
        self.setIcon(icon)
        self.setIconSize(QSize(40, 40))  # Устанавливаем начальный размер иконки
        self.setAcceptDrops(False)  # Кнопка — только источник перетаскивания

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Начало перетаскивания
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText("icon")  # Передаем текст "icon" как идентификатор
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)


class ResizableMovableLabel(QLabel):
    """Класс для элементов, которые можно перемещать и растягивать в рабочей области"""

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio))
        self.setFixedSize(60, 60)
        self.is_resizing = False
        self.is_moving = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Если клик в правом нижнем углу, начинаем изменение размера
            if (self.width() - 10 <= event.x() <= self.width() and
                    self.height() - 10 <= event.y() <= self.height()):
                self.is_resizing = True
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                # Иначе начинаем перемещение объекта
                self.is_moving = True
                self.offset = event.pos()
                self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, event):
        if self.is_resizing:
            # Изменяем размер элемента
            new_width = max(30, event.x())
            new_height = max(30, event.y())
            self.setPixmap(self.pixmap().scaled(new_width, new_height, Qt.KeepAspectRatio))
            self.setFixedSize(new_width, new_height)
        elif self.is_moving:
            # Перемещаем элемент
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        # Завершаем изменение размера или перемещение
        if self.is_resizing:
            self.is_resizing = False
        elif self.is_moving:
            self.is_moving = False
        self.setCursor(Qt.ArrowCursor)


class DropArea(QLabel):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #a9a9a9; border-radius: 5px;")  # Темный фон рабочей области
        self.setAlignment(Qt.AlignCenter)
        self.dropped_items = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Создаем растягиваемый и перемещаемый элемент с пустым изображением
        pixmap = QPixmap(60, 60)
        pixmap.fill(QColor("lightgray"))
        new_label = ResizableMovableLabel(pixmap, self)

        # Центрируем новый элемент в месте сброса
        drop_pos = event.pos()
        new_label.move(drop_pos - QPoint(new_label.width() // 2, new_label.height() // 2))
        new_label.show()

        self.dropped_items.append(new_label)
        event.acceptProposedAction()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Установка основного окна
        self.setWindowTitle("UML EDITOR")
        self.setGeometry(100, 100, 800, 600)

        # Добавление меню
        menu_bar = QMenuBar(self)
        file_menu = QMenu("Файл", self)
        stats_menu = QMenu("Статистика", self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(stats_menu)
        self.setMenuBar(menu_bar)

        # Основной виджет
        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель (тулбар)
        toolbar_widget = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_widget)

        toolbar_layout.addWidget(QLabel("Toolbar"))

        # Создание пустых иконок-заполнителей
        icon_placeholder = QPixmap(40, 40)
        icon_placeholder.fill(QColor("lightgray"))

        # Добавление пустых иконок в тулбар
        for _ in range(7):
            toolbar_layout.addWidget(DraggableButton(icon_placeholder, self))

        toolbar_layout.addStretch()

        main_layout.addWidget(toolbar_widget)

        # Рабочая область
        self.drop_area = DropArea()
        main_layout.addWidget(self.drop_area, 1)

        self.setCentralWidget(central_widget)

        # Нижняя панель
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        # Добавление элементов на нижнюю панель
        btn_pay = QPushButton("Оплата заказа", self)
        btn_find= QPushButton("Поиск товара", self)

        status_bar.addWidget(btn_pay)
        status_bar.addWidget(btn_find)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())