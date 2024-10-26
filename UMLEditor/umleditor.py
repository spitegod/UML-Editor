import os
from PyQt5 import QtCore, QtGui, QtWidgets
from Static import Ui_StaticWidget  # Импортируем класс Ui_StaticWidget
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtCore import pyqtSignal  # Импортируем pyqtSignal

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

class Ui_MainWindow(QtWidgets.QMainWindow):
    time_updated = pyqtSignal(str)  # Создаем сигнал с параметром типа str

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.last_time = "00:00:00"  # Изначальное значение времени

        # Настраиваем таймер для обновления времени каждую секунду
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.increment_time)  # Соединяем таймер с функцией обновления времени
        self.timer.start(1000)  # Запускаем таймер с интервалом в 1 секунду

    def increment_time(self):
        """Метод для увеличения времени на 1 секунду и отправки обновленного значения."""
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
        
        self.time_updated.emit(self.last_time)  # Отправляем обновленное значение


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
        self.label = QtWidgets.QLabel(self.ToolBarBox)
        self.label.setText("")
        #Без понятия, что здесь должно быть
        self.label.setPixmap(QtGui.QPixmap("../Downloads/Decision-node-and-merge-node-1.png"))
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        # startstate.png
        self.label_2 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_2.setText("")
        #Здесь надо вписать полный путь для startstate.png
        self.label_2.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/startstate.png"))
        self.label_2.setScaledContents(False)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        # finalstate.png
        self.label_3 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_3.setText("")
        #Здесь надо вписать полный путь для finalstate.png"
        self.label_3.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/finalstate.png"))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        # merge.png
        self.label_5 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_5.setText("")
        #Здесь надо вписать полный путь для merge.png
        self.label_5.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/merge.png")) 
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 1, 1, 1)

        # Signal-sending.png
        self.label_7 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_7.setText("")
        #Здесь надо вписать полный путь для Signal-sending.png
        self.label_7.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/Signal-sending.png")) 
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)

        # Signal-receipt.png
        self.label_8 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_8.setText("")
        #Здесь надо вписать полный путь для Signal-receipt.png
        self.label_8.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/Signal-receipt.png")) 
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 1, 1, 1)

        # arrowsolid.png
        self.label_9 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_9.setText("")
        #Здесь надо вписать полный путь для arrowsolid.png
        self.label_9.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/arrowsolid.png")) 
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 2, 2, 1, 1)

        # synchronize.png
        self.label_4 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_4.setText("")
        #Здесь надо вписать полный путь для synchronize.png
        self.label_4.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/synchronize.png")) 
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        # ctivestate.png
        self.label_6 = QtWidgets.QLabel(self.ToolBarBox)
        self.label_6.setText("")
        #Здесь надо вписать полный путь для ctivestate.png
        self.label_6.setPixmap(QtGui.QPixmap("C:/Users/79050/Desktop/Качество и надежность ИС/UMLEditor/imgs/activestate.png")) 
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)

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
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 18))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
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

        # self.label = QtWidgets.QLabel(self.ToolBarBox)
        # pixmap = QtGui.QPixmap("imgs\startstate.png")
        # if pixmap.isNull():
        #     print("Ошибка загрузки изображения: imgs/startstate.png")
        # self.label.setPixmap(pixmap)
        # self.label.setScaledContents(True)
        # self.label.adjustSize()


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

        # Создаём невидимый QLabel для записи времени
        self.Start_Time = QtWidgets.QLabel(self.centralwidget)
        self.Start_Time.setGeometry(QtCore.QRect(100, 100, 200, 50))  # Устанавливаем размер и позицию
        self.Start_Time.setAlignment(QtCore.Qt.AlignCenter)  # Центрируем текст
        self.Start_Time.setFont(QtGui.QFont("Helvetica", 16))  # Устанавливаем шрифт и размер
        self.Start_Time.setText("00:00:00")  # Устанавливаем начальное значение времени


        # pixmap = QtGui.QPixmap("imgs/startstate.png")
        # if pixmap.isNull():
        #     print(f"Ошибка загрузки изображения: path/to/image.png")
        #     self.label_2.setPixmap(pixmap)
        #     self.label_2.setScaledContents(True)
        #     self.label.adjustSize()  # Автоматически настраивает размер QLabel под изображение

        #Таймер

        #Инициализируем переменные для секундомера
        self.running = False
        self.elapsed_time = QTime(0, 0)

        self.timer = QTimer()

        Start_Time = "00:00:00"
        self.Start_Time.setVisible(False)
        self.timer.timeout.connect(self.update_time)

        self.start()


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    #Ниже 4 функции - реализация работы таймера

    def start(self):
        if not self.running:  # Запускаем таймер, только если он не запущен
            self.running = True
            self.timer.start(1000)  # Интервал 1000 мс (1 секунда)

    def stop(self):
        if self.running:  # Останавливаем таймер
            self.running = False
            self.timer.stop()
            self.last_time = self.Start_Time.text()  # Сохраняем текущее значение времени перед остановкой


    def reset(self):
        self.elapsed_time = QTime(0, 0)  # Сбрасываем время
        #self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)  # Увеличиваем время на 1 секунду
        time_str = self.elapsed_time.toString("hh:mm:ss")  # Преобразуем время в строку
        self.Start_Time.setText(time_str)  # Обновляем отображение времени
        self.last_time = time_str  # Сохраняем последнее значение времени

    #2 функции для передачи времени в UI_StaticWidget

    def update_last_time(self, new_time):
        """Метод для обновления last_time и отправки сигнала с новым значением."""
        self.last_time = new_time
        self.time_updated.emit(self.last_time)  # Отправляем сигнал с обновленным временем

    def get_last_time(self):
        return self.last_time

    #Отображение окна статистики
    def show_static_widget(self):
        self.static_widget = QtWidgets.QWidget()  # Создаем новый виджет
        self.static_ui = Ui_StaticWidget()  # Создаем экземпляр Ui_StaticWidget
        #self.static_ui = Ui_StaticWidget(self.get_last_time())  # Передаем last_time в Ui_StaticWidget

        # Подключаем слот StaticWidget к сигналу time_updated
        self.time_updated.connect(self.static_ui.update_timework)
        
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
        self.action.setText(_translate("MainWindow", "Открыть"))
        self.action_2.setText(_translate("MainWindow", "Сохранить"))
        self.action_3.setText(_translate("MainWindow", "Сохранить как"))
        self.action_PNG.setText(_translate("MainWindow", "Экспорт в PNG"))
        self.action_4.setText(_translate("MainWindow", "Создать"))
        self.action_Statystics.setText(_translate("MainWindow", "Запустить статистику"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
