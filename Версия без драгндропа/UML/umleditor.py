import os
import sys
import json
from math import *
from PyQt5 import QtCore, QtGui, QtWidgets
from Static import Ui_StaticWidget  # Импортируем класс Ui_StaticWidget
from uml_elements import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QShortcut, QMessageBox, QUndoCommand, QUndoStack, QMenu, QMenuBar
from PyQt5.QtCore import QTimer, QTime, QDateTime
from PyQt5.QtCore import pyqtSignal  # Импортируем pyqtSignal
from PyQt5.QtCore import Qt, QPointF, QLineF
from PyQt5.QtGui import QPen, QBrush, QPainterPath, QKeySequence

from PyQt5 import QtWidgets, QtGui, QtCore

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

class My_GraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, reset_time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selection_rect = None  # Прямоугольник для выделения
        self.start_pos = None  # Начальная позиция для выделения
        self.is_dragging = False  # Флаг, указывающий, что элемент перетаскивается
        # self.clicks = []  # Список для хранения информации о кликах
        self.reset_time = reset_time
        # self.selected_order = []
        # self.undo_stack = QUndoStack()

        

    
    
    def drawBackground(self, painter, rect):
        # Включаем сглаживание
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)  # Для сглаживания изображения

        super().drawBackground(painter, rect)

    def mousePressEvent(self, event):

        self.reset_time.reset_inaction()
        # self.clicks.append(event.scenePos())
        # Проверяем, перетаскивается ли какой-то элемент
        if self.itemAt(event.scenePos(), QtGui.QTransform()) is not None:
            self.is_dragging = True  # Если элемент найден, устанавливаем флаг перетаскивания
        else:
            self.is_dragging = False  # Если нет — снимаем флаг

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
        self.reset_time.reset_inaction()
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
        # self.count_elements = count_elements #Длинна списка objectS_


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







class Ui_MainWindow(QtWidgets.QMainWindow):
    time_updated = pyqtSignal(str, str, str)  # Создаем сигнал с параметром типа str для передачи запущенного времени
    update_last_timeSW = pyqtSignal(str, str, str)  # Создаем сигнал для передачи последнего значения времени
    count_objectS = pyqtSignal(int) # Создаем сигнал о подсчете количества объектов на сцене для отображения его в статистике
    user_actions = pyqtSignal(str, int, str, str, str, str) # Создаем сигнал который учитывает дейсвтия пользователя на сцене для обновления информации на окне статистики

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
        self.button.setIconSize(QtCore.QSize(100, 100))  # Установка размера иконки (при необходимости)
        self.button.setObjectName("button")
        self.gridLayout.addWidget(self.button, 0, 0, 1, 1)
        self.button.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # startstate.png
        self.button_2 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_2.setIcon(QtGui.QIcon("imgs/startstate.png"))
        self.button_2.setIconSize(QtCore.QSize(100, 100))
        self.button_2.setObjectName("button_2")
        self.gridLayout.addWidget(self.button_2, 0, 1, 1, 1)
        self.button_2.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # finalstate.png
        self.button_3 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_3.setIcon(QtGui.QIcon("imgs/finalstate.png"))
        self.button_3.setIconSize(QtCore.QSize(100, 100))
        self.button_3.setObjectName("button_3")
        self.gridLayout.addWidget(self.button_3, 0, 2, 1, 1)
        self.button_3.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # merge.png
        self.button_4 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_4.setIcon(QtGui.QIcon("imgs/merge.png"))
        self.button_4.setIconSize(QtCore.QSize(100, 100))
        self.button_4.setObjectName("button_4")
        self.gridLayout.addWidget(self.button_4, 1, 1, 1, 1)
        self.button_4.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Signal-sending.png
        self.button_5 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_5.setIcon(QtGui.QIcon("imgs/Signal-sending.png"))
        self.button_5.setIconSize(QtCore.QSize(100, 100))
        self.button_5.setObjectName("button_5")
        self.gridLayout.addWidget(self.button_5, 2, 0, 1, 1)
        self.button_5.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # Signal-receipt.png
        self.button_6 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_6.setIcon(QtGui.QIcon("imgs/Signal-receipt.png"))
        self.button_6.setIconSize(QtCore.QSize(100, 100))
        self.button_6.setObjectName("button_6")
        self.gridLayout.addWidget(self.button_6, 2, 1, 1, 1)
        self.button_6.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")


        # arrowsolid.png
        self.button_7 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_7.setIcon(QtGui.QIcon("imgs/arrowsolid.png"))
        self.button_7.setIconSize(QtCore.QSize(100, 100))
        self.button_7.setObjectName("button_7")
        self.gridLayout.addWidget(self.button_7, 2, 2, 1, 1)
        self.button_7.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")

        # synchronize.png
        self.button_8 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_8.setIcon(QtGui.QIcon("imgs/synchronize.png"))
        self.button_8.setIconSize(QtCore.QSize(100, 100))
        self.button_8.setObjectName("button_8")
        self.gridLayout.addWidget(self.button_8, 1, 0, 1, 1)
        self.button_8.setStyleSheet("""
        QPushButton {
            border:none;                      }
""")


        # ativestate.png
        self.button_9 = QtWidgets.QPushButton(self.ToolBarBox)
        self.button_9.setIcon(QtGui.QIcon("imgs/activestate.png"))
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
        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
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
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)
        self.menu_2.addAction(self.action_Statystics)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction()) #Тестовое меню таймера

        self.action_2.triggered.connect(lambda: self.save_to_file(filepath="diagram.chep"))
        self.action_3.triggered.connect(self.save_as)
        self.action.triggered.connect(self.open_file)
        self.action_exit.triggered.connect(self.close_application)

        self.menu_3.addAction(self.action_time_start) #Добавление вкладок на тестовое меню для таймера
        self.menu_3.addAction(self.action_time_stop)
        self.menu_3.addAction(self.action_time_reset)

        # Создаём невидимый QLabel для записи времени
        self.Start_Time = QtWidgets.QLineEdit(self.centralwidget)
        self.Start_Time.setGeometry(QtCore.QRect(100, 100, 200, 50))  # Устанавливаем размер и позицию
        self.Start_Time.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
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

        #Второй таймер для остановки основного таймера если пользователь бездействует
        self.Time_inaction = QtWidgets.QLineEdit(self.centralwidget)
        self.Time_inaction.setGeometry(QtCore.QRect(200, 200, 200, 50))  # Устанавливаем размер и позицию
        self.Time_inaction.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
        self.Time_inaction.setText("00:00:00")  # Устанавливаем начальное значение времени
        self.Time_inaction.setReadOnly(True)
        self.Time_inaction.setVisible(False) #По умолчанию всегда невиден

        self.running_inaction = False
        self.elapsed_Time_inaction = QTime(0, 0)

        self.timer_inaction = QTimer()
        self.timer_inaction.timeout.connect(self.update_time)


        #self.Start_Time.textChanged.connect(self.update_time)

        self.action_time_start.triggered.connect(self.start)
        self.action_time_stop.triggered.connect(self.stop)
        self.action_time_reset.triggered.connect(self.reset)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        # Настроим кастомную сцену для рисования
        self.scene_ = My_GraphicsScene(self)  # Используем кастомную сцену
        self.graphicsView.setScene(self.scene_)  # Устанавливаем сцену в QGraphicsView
        # if self.scene_.has_clicks: self.reset_inaction()

        # Кнопки тулбара
        self.button.clicked.connect(self.draw_diamond)
        self.button_2.clicked.connect(self.draw_circle)
        self.button_3.clicked.connect(self.draw_circle_2)
        self.button_9.clicked.connect(self.draw_rounded_rectangle)
        self.button_5.clicked.connect(self.draw_pentagon_signal)
        self.button_6.clicked.connect(self.draw_pentagon_reverse)

        #Проверка превышение количества объектов на сцене
        self.button.clicked.connect(self.message_overcrowed_objectS)
        self.button_2.clicked.connect(self.message_overcrowed_objectS)
        self.button_3.clicked.connect(self.message_overcrowed_objectS)
        self.button_9.clicked.connect(self.message_overcrowed_objectS)
        self.button_5.clicked.connect(self.message_overcrowed_objectS)

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

        # self.connect_objectS = QShortcut(QKeySequence("T"), self.graphicsView)
        # self.connect_objectS.activated.connect(self.disconnect_nodes)

         # Обновляем сцену после инициализации
        self.scene_.update()  # Перерисовываем сцену

        # # Пользовательская информация
        self.user_ = User("User1", 0, self.time_now, self.get_time_for_user(self.last_time))
        self.user_.add_action("Создана диаграмма UML", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))


        # # self.static_widget = QtWidgets.QWidget()
        # self.static_ui = Ui_StaticWidget()  # Создаем экземпляр Ui_StaticWidget

        # self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))
        # self.user_actions.connect(self.static_ui.uptade_static)

    def save_to_file(self, filepath=None):
        """Сохранение текущей диаграммы в файл формата chep."""
        if not filepath:  # Если путь не задан, запрашиваем его у пользователя
            options = QtWidgets.QFileDialog.Options()
            filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "CHEP Files (*.chep);;All Files (*)", options=options
            )
            if not filepath:
                return

        data = {"items": []}
        for item in self.scene_.items():
            if isinstance(item, QtWidgets.QGraphicsItem):
                data["items"].append(self.serialize_item(item))

        try:
            with open(filepath, "w") as file:
                json.dump(data, file, indent=4)
            print("Файл сохранён:", filepath)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def save_as(self):
        """Сохранить как. Всегда предлагает выбрать путь для сохранения."""
        self.save_to_file()  # Просто вызываем save_to_file без пути

    def open_file(self):
        """Открытие файла формата chep."""
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
            "line_width": None               # Толщина линии (для Arrow)
        }

        # Заполняем структуру в зависимости от типа элемента
        if isinstance(item, Decision):  # Ромб
            base_data["size"] = item.size

        elif isinstance(item, StartEvent):  # Круг (начало)
            rect = item.rect()
            base_data["radius"] = rect.width() / 2

        elif isinstance(item, EndEvent):  # Круг с внутренним кругом (конец)
            rect = item.rect()
            base_data["radius"] = rect.width() / 2
            base_data["inner_radius_ratio"] = item.inner_radius_ratio

        elif isinstance(item, ActiveState):  # Прямоугольник с закругленными углами
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()
            base_data["radius"] = rect.width() / 16
            base_data["text"] = item.text_item.toPlainText() if hasattr(item, "text_item") else None

        elif isinstance(item, SignalSending):  # Пентагон (сигнал отправки)
            rect = item.boundingRect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()

        elif isinstance(item, SignalReceipt):  # Пентагон (сигнал получения)
            rect = item.boundingRect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()

        elif isinstance(item, Arrow):  # Стрелка
            base_data["start_node"] = (item.node1.x(), item.node1.y())
            base_data["end_node"] = (item.node2.x(), item.node2.y())
            pen = item.pen()
            base_data["color"] = pen.color().name()
            base_data["line_width"] = pen.width()

        elif isinstance(item, QtWidgets.QGraphicsEllipseItem):  # Простой круг
            rect = item.rect()
            base_data["width"] = rect.width()
            base_data["height"] = rect.height()

        # Возвращаем структуру со всеми ключами
        return base_data


    

    def close_application(self):
        """Обработка выхода из приложения через пункт меню."""
        self.close()


    def closeEvent(self, event):
        print('Вызвано')
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
    
    def message_overcrowed_objectS(self):
        if len(self.objectS_) == 11:
            self.reset_inaction() #Сбрасыем второй таймер
            self.count_objectS.emit(len(self.objectS_) - 1)
            self.scene_.removeItem(self.objectS_[len(self.objectS_) - 1])
            del self.objectS_[len(self.objectS_) - 1]
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Превышено максимальное значение элементов")
            msgBox.setWindowTitle("Предупреждение")
            msgBox.setStandardButtons(QMessageBox.Ok )
            # msgBox.buttonClicked.connect(msgButtonClick)

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

    def draw_diamond(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра и размер ромба
        x, y, size = 200, 200, 50  # Пример координат и размера
        diamond = Decision(x, y, size)
        self.scene_.addItem(diamond)  # Добавляем ромб на сцену


        self.objectS_.append(diamond)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{diamond.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))
        # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок


    def draw_circle(self):
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        self.reset_inaction() #Сбрасыем второй таймер
        x, y, radius = 200, 200, 30  # Пример: рисуем круг в центре с радиусом 50
        circle = StartEvent(x, y, radius)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{circle.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))
        # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_circle_2(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Вставляем круг на сцену
        # Координаты центра и радиус круга
        x, y, radius, into_radius = 200, 200, 30, 0.5  # Пример: рисуем круг в центре с радиусом 50
        circle = EndEvent(x,y,radius, into_radius)
        self.scene_.addItem(circle)  # Добавляем круг на сцену

        self.objectS_.append(circle)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{circle.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))
        # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок


    def draw_rounded_rectangle(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, width, height, radius = 200, 200, 100, 60, 15  # Пример координат, размера и радиуса
        rounded_rect = ActiveState(x, y, width, height, radius)
        self.scene_.addItem(rounded_rect)  # Добавляем закругленный прямоугольник на сцену

        self.objectS_.append(rounded_rect)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{rounded_rect.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))

        # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок


    def draw_pentagon_signal(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, size = 200, 200, 100  # Пример координат, размера и радиуса
        pentagon = SignalSending(x, y, 60, 150)
        self.scene_.addItem(pentagon)  # Добавляем закругленный прямоугольник на сцену

        self.objectS_.append(pentagon)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))

        # # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок

    def draw_pentagon_reverse(self):
        self.reset_inaction() #Сбрасыем второй таймер
        # Координаты центра, ширина, высота и радиус закругления
        x, y, size = 200, 200, 100  # Пример координат, размера и радиуса
        pentagon = SignalReceipt(x, y, 60, 200)
        pentagon.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.scene_.addItem(pentagon)  # Добавляем закругленный прямоугольник на сцену

        self.objectS_.append(pentagon)

        print("Количество объектов на сцене - ", len(self.objectS_))
        self.count_objectS.emit(len(self.objectS_))

        self.user_.add_action(f"Добавлен элемент '{pentagon.__class__.__name__}'", self.get_current_Realtime())
        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))

        # # Обновляем стрелки, если это необходимо
        # for arrow in self.objectS_:
        #     if isinstance(arrow, Arrow):
        #         arrow.update_arrow()  # Перерисовываем стрелку для всех стрелок


    def add_edge(self):
        self.reset_inaction() #Сбрасыем второй таймер
        selected_nodes = [object_ for object_ in self.objectS_ if object_.isSelected()]

        if len(selected_nodes) == 2:
            node1, node2 = selected_nodes

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
            self.scene_.addItem(arrow)  # Добавляем стрелку на сцену


            # Привязываем стрелку к обоим узлам
            node1.add_arrow(arrow)
            node2.add_arrow(arrow)

            # Сохраняем стрелку в списке объектов
            # self.objectS_.append(arrow)
            # print("Количество объектов на сцене - ", len(self.objectS_))
            

            # Обновляем стрелку сразу после добавления
            arrow.update_arrow()  # Обновляем стрелку вручную, если нужно
            self.scene_.update()  # Перерисовываем сцену



    # def handle_selection(self, selected_item):
    #     # Добавляем логику для отслеживания выбора
    #     if selected_item not in self.selected_order:
    #         self.selected_order.append(selected_item)
    #     else:
    #         # Перемещаем выбранный элемент в конец списка
    #         self.selected_order.remove(selected_item)
    #         self.selected_order.append(selected_item)


    
    def select_all_item(self):
        self.reset_inaction()
        for item in self.scene_.items():
            # Проверяем может ли элемент выделяться
            if isinstance(item, QtWidgets.QGraphicsItem):
                item.setSelected(True)

    def disconnect_nodes(self, node1, node2):
        if hasattr(node1, 'arrows') and hasattr(node2, 'arrows'):
            for arrow in node1.arrows[:]:
                if (arrow.node1 == node2 or arrow.node2 == node2) and arrow in node2.arrows:
                    if arrow.scene():  # Удаляем из сцены, если стрелка добавлена
                        self.scene_.removeItem(arrow)
                    
                    # Удаляем стрелку из списков arrows для узлов
                    if arrow in node1.arrows:
                        node1.arrows.remove(arrow)
                    if arrow in node2.arrows:
                        node2.arrows.remove(arrow)
                    del arrow



                
    def delete_selected_item(self):
        self.reset_inaction()  # Сбрасываем второй таймер
        selected_items = self.scene_.selectedItems()

        for item in selected_items:
            if isinstance(item, (StartEvent, Decision, EndEvent, ActiveState, SignalSending, SignalReceipt)):
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
                self.user_actions.emit(
                    self.user_.nickname, self.user_.user_id,
                    self.user_.start_work, self.user_.end_work,
                    next(reversed(self.user_.action_history)),
                    next(reversed(self.user_.action_history.values()))
                )

        self.count_objectS.emit(len(self.objectS_))
        self.scene_.update()  # Перерисовываем сцену


    # def count_objectS(self):
    #     return len(self.objectS_)



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

            self.running_inaction = False
            self.timer_inaction.stop()

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
        self.elapsed_Time_inaction = self.elapsed_Time_inaction.addSecs(1)
        time_str2 = self.elapsed_Time_inaction.toString("hh:mm:ss")
        self.Start_Time.setText(time_str)  # Обновляем отображение времени
        self.last_time = time_str  # Сохраняем последнее значение времени
        self.Time_inaction.setText(time_str2)

        if self.Time_inaction.text() == "00:00:30":
            self.stop()

    def reset_inaction(self):
        self.elapsed_Time_inaction = QTime(0, 0)  # Сбрасываем время
        # self.Time_inaction.setText("00:00:00")
        self.start()
        #self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    # def stop_inaction(self):
    #     if self.running_inaction:  # Останавливаем таймер
    #         self.running = False
    #         self.running_inaction = False
    #         self.timer_inaction.stop()
    #         self.timer_2.stop()
    #         self.last_time = self.Start_Time.text()  # Сохраняем текущее значение времени перед остановкой

    #         print("Таймер был остановлен из-за бездействий пользователя")

    #         self.time_updated.emit(self.today, self.last_time, self.time_now)  # Отправляем сигнал с зафиксированным временем
            # changed_time = QDateTime.fromString(self.last_time, "HH:mm:ss")
            # print(changed_time)

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
        self.get_time_for_user(self.last_time)
        # self.update_last_timeSW.emit(self.last_time)

    def get_time_for_user(self, last_time):
        return last_time


    

        self.static_widget = QtWidgets.QWidget()  # Создаем новое окно
        self.static_ui = Ui_StaticWidget()  # Создаем экземпляр Ui_StaticWidget


    def load_from_data(self, data):
        self.scene_.clear()  # Очищаем сцену перед загрузкой новых данных

        for item_data in data["items"]:
            item_type = item_data["type"]
            position = item_data["position"]

            # Создание объектов в зависимости от типа
            if item_type == "Decision":
                size = item_data.get("size", 50)  # Достаём "size" с умолчанием
                item = Decision(*position, size)
                self.scene_.addItem(item)

            elif item_type == "StartEvent":
                radius = item_data.get("radius", 30)  # Достаём "radius" с умолчанием
                item = StartEvent(*position, radius)
                self.scene_.addItem(item)

            elif item_type == "EndEvent":
                radius = item_data.get("radius", 30)
                inner_radius_ratio = item_data.get("inner_radius_ratio", 0.5)
                item = EndEvent(*position, radius, inner_radius_ratio)
                self.scene_.addItem(item)

            elif item_type == "ActiveState":
                width = item_data.get("width", 100)
                height = item_data.get("height", 50)
                radius = item_data.get("radius", 10)
                text = item_data.get("text", "")
                item = ActiveState(*position, width, height, radius)
                item.text_item.setPlainText(text)
                self.scene_.addItem(item)

            elif item_type == "SignalSending":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                item = SignalSending(*position, width, height)
                self.scene_.addItem(item)

            elif item_type == "SignalReceipt":
                width = item_data.get("width", 60)
                height = item_data.get("height", 40)
                item = SignalReceipt(*position, width, height)
                self.scene_.addItem(item)

            elif item_type == "Arrow":
                start_node = item_data.get("start_node", (0, 0))
                end_node = item_data.get("end_node", (0, 0))
                color = item_data.get("color", "#000000")
                line_width = item_data.get("line_width", 1)

                # Создаём стрелку и настраиваем её стиль
                item = Arrow(QPointF(*start_node), QPointF(*end_node))
                pen = item.pen()
                pen.setColor(QtGui.QColor(color))
                pen.setWidth(line_width)
                item.setPen(pen)

                self.scene_.addItem(item)

            elif item_type == "QtWidgets.QGraphicsEllipseItem":
                width = item_data.get("width", 60)
                height = item_data.get("height", 60)
                rect = QRectF(-width / 2, -height / 2, width, height)
                item = QtWidgets.QGraphicsEllipseItem(rect)
                item.setPos(*position)
                self.scene_.addItem(item)


    #Отображение окна статистики
    def show_static_widget(self):
        

        self.user_actions.emit(self.user_.nickname, self.user_.user_id, self.user_.start_work, self.user_.end_work, next(reversed(self.user_.action_history)), next(reversed(self.user_.action_history.values())))
        self.user_actions.connect(self.static_ui.uptade_static)
        #self.static_ui = Ui_StaticWidget(self.get_last_time())   # Передаем last_time в Ui_StaticWidget
        # Подключаем слот StaticWidget к сигналу time_updated
        self.time_updated.connect(self.static_ui.update_timeworkSW)
        self.update_last_timeSW.connect(self.static_ui.update_last_timeSW)
        self.static_ui.update_timeworkSW(self.today, self.Start_Time.text(), self.time_now)
        self.static_ui.accept_today(self.today, self.time_now, self.last_time)
        self.update_last_timeSW.emit(self.today, self.last_time, self.time_now)  # Отправляем значение при открытии
        # self.static_ui.update_timeworkSW(self.last_time)
        # self.timeStop_ChangedSignal.connect(self.static_ui.receive_text)
        self.count_objectS.connect(self.static_ui.get_count_objectS)
        self.count_objectS.emit(len(self.objectS_))
        
        self.static_ui.setupUi(self.static_widget)  # Настраиваем новый виджет
        self.static_widget.setWindowTitle("Статистика")  # Заголовок нового окна
        # self.static_widget.resize(800, 600)  # Размер нового окна
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
        self.action_exit.setText(_translate("MainWindow", "Выход"))
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