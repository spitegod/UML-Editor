import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from Static import Ui_StaticWidget  # Импортируем класс Ui_StaticWidget
from PyQt5.QtCore import QTimer, QTime, QDateTime
from PyQt5.QtCore import pyqtSignal, QByteArray, QDataStream, QIODevice, QPoint, Qt, QMimeData  # Импортируем pyqtSignal
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QDrag


#НАЧАЛО ПЕРЕДЕЛЫВАНИЯ ПОД QFRAME
class ToolbarWidget(QFrame):
    def __init__(self, parent=None):
        super(ToolbarWidget, self).__init__(parent)
        self.setMinimumSize(200, 400)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)

        # Устанавливаем сеточный layout для упорядочивания иконок
        self.grid_layout = QGridLayout(self)
        self.add_icons()

    def add_icons(self):
        # Путь к папке с изображениями
        image_folder = r"C:\Новая папка\UML-Editor\UMLEditor\imgs"
        # Список иконок с координатами для сетки (порядок добавления)
        icons = [
            "startstate.png", "finalstate.png", "activestate.png",
            "decision.png", "merge.png", "synchronize.png",
            "Signal-sending.png", "Signal-receipt.png", "arrowsolid.png"
        ]

        # Добавляем иконки в сетку
        for i, icon_name in enumerate(icons):
            icon_path = f"{image_folder}/{icon_name}"
            if not QPixmap(icon_path).isNull():
                icon_label = QLabel(self)
                icon_label.setPixmap(QPixmap(icon_path))
                
                # Располагаем иконки по строкам и столбцам (по 3 в строке)
                row = i // 3
                col = i % 3
                self.grid_layout.addWidget(icon_label, row, col)
            else:
                print(f"Изображение {icon_path} не найдено")
    
    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            return

        pixmap = QPixmap(child.pixmap())

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap << QPoint(event.pos() - child.pos())

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())
        
        drag.exec_(Qt.CopyAction)


class WorkspaceWidget(QFrame):
    def __init__(self, parent=None):
        super(WorkspaceWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            itemData = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)

            pixmap = QPixmap()
            offset = QPoint()
            dataStream >> pixmap >> offset

            newIcon = DraggableLabel(self)
            newIcon.setPixmap(pixmap)
            newIcon.move(event.pos() - offset)
            newIcon.show()

            event.acceptProposedAction()
        else:
            event.ignore()

#КОНЕЦ ПЕРЕДЕЛЫВАНИЯ ПОД QFRAME

class DraggableLabel(QLabel):
    def __init__(self, parent=None):
        super(DraggableLabel, self).__init__(parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mimeData = QMimeData()

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << self.pixmap() << QPoint(event.pos())

            mimeData.setData('application/x-dnditemdata', itemData)
            drag.setMimeData(mimeData)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())

            if drag.exec_(Qt.MoveAction) == Qt.MoveAction:
                self.close()


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

class Ui_MainWindow(QtWidgets.QMainWindow):
    time_updated = pyqtSignal(str, str, str)  # Создаем сигнал с параметром типа str для передачи запущенного времени
    update_last_timeSW = pyqtSignal(str, str, str)  # Создаем сигнал для передачи последнего значения времени
    # Создаем сигнал для передачи данных на моменте остановки таймера
    # timeStop_ChangedSignal = QtCore.pyqtSignal(str)

    # def __init__(self):
    #     super().__init__()


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
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Заменяем ToolBarBox на ToolbarWidget
        self.toolbar = ToolbarWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.toolbar)

        # Заменяем graphicsView на WorkspaceWidget
        self.workspace = WorkspaceWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.workspace)

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

    # time_stopped = pyqtSignal(str)  # Сигнал с последним временем

    # def stop_timer(self):
    #     last_time = self.elapsed_time.toString("hh:mm:ss")
    #     self.time_stopped.emit(last_time)  # Передаем последнее значение времени через сигнал

    #Функция для передачи времени в UI_StaticWidget

    # def update_last_timeSW(self, new_time):
    #     """Метод для обновления last_time и отправки сигнала с новым значением."""
    #     self.last_time = new_time
    #     self.time_updated.emit(self.last_time)  # Отправляем сигнал с обновленным временем

    # def get_last_time(self):
    #     return self.elapsed_time.toString("hh:mm:ss")

    # def get_last_time(self):
    #     return self.last_time

    #Отображение окна статистики
    def show_static_widget(self):

        # self.Time_ToStatic = self.Start_Time.text()

        # lt_for_timeworkend = QDateTime.fromString(self.last_time, "HH:mm:ss")


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