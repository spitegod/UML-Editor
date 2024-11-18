import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, QDate, QTime

class Ui_StaticWidget(QtWidgets.QWidget): 

    
    def __init__(self):
        super().__init__()

        #Linedit начало времени работы
        self.dateTimeEdit_Start = QtWidgets.QLineEdit(self)
        self.dateTimeEdit_Start.setReadOnly(True)
        self.dateTimeEdit_Start.setInputMask("00.00.0000 00:00:00")
        self.dateTimeEdit_Start.setAlignment(QtCore.Qt.AlignCenter)
        self.dateTimeEdit_Start.setObjectName("dateTimeEdit_Start")

        #Lineedit в котором записывается время работы
        self.lineEdit_timework = QtWidgets.QLineEdit(self)
        self.lineEdit_timework.setReadOnly(True)
        self.lineEdit_timework.setInputMask("00:00:00")
        self.lineEdit_timework.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_timework.setObjectName("lineEdit_timework")

        #Lineedit конец времени работы
        self.dateTimeEdit_End = QtWidgets.QLineEdit(self)
        self.dateTimeEdit_End.setReadOnly(True)
        self.dateTimeEdit_End.setInputMask("00.00.0000 00:00:00")
        self.dateTimeEdit_End.setAlignment(QtCore.Qt.AlignCenter)
        self.dateTimeEdit_End.setObjectName("dateTimeEdit_End")

        #lineeit о количестве объектов на сцене
        self.label_count_el = QtWidgets.QLineEdit(self)
        self.label_count_el.setReadOnly(True)
        self.label_count_el.setObjectName("label_count_el")

        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

    

    def setupUi(self, StaticWidget):  # Используем StaticWidget вместо StaticWindow

        import umleditor

        # Создаём экземпляр MainWindow и вызываем get_last_time()
        main_window = umleditor.Ui_MainWindow()  # Создаём экземпляр класса Ui_MainWindow

        StaticWidget.setObjectName("StaticWidget")
        StaticWidget.setWindowModality(QtCore.Qt.NonModal)
        StaticWidget.resize(316, 157)
        StaticWidget.setFixedSize(850, 300)  # Фиксируем размер окна
        # StaticWidget.setStyleSheet("background-color: rgb(233, 233, 233);")
        
        self.gridLayout = QtWidgets.QGridLayout(StaticWidget)  # Основной layout для StaticWidget
        self.gridLayout.setObjectName("gridLayout")
        
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        # Заголовок "Статистика"
        # self.label = QtWidgets.QLabel(StaticWidget)
        # self.label.setObjectName("label")
        # self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        
        # Основная рабочая область
        self.horizontalLayout_workarea = QtWidgets.QHBoxLayout()
        self.horizontalLayout_workarea.setObjectName("horizontalLayout_workarea")
        
        # Блок выбора пользователя
        self.verticalLayout_UserChoose = QtWidgets.QVBoxLayout()
        self.verticalLayout_UserChoose.setObjectName("verticalLayout_UserChoose")
        
        self.label_2 = QtWidgets.QLabel(StaticWidget)
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_UserChoose.addWidget(self.label_2)
        
        self.listWidget_Users = QtWidgets.QListWidget(StaticWidget)
        self.listWidget_Users.setObjectName("listWidget_Users")
        self.listWidget_Users.setFixedWidth(100)
        for username in ["User1"]:
            item = QtWidgets.QListWidgetItem(username)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.listWidget_Users.addItem(item)
        # self.listWidget_Users.setItemAlignment(QtCore.Qt.AlignCenter)
        self.listWidget_Users.setStyleSheet("""
QListWidget {
            border: none;
            background: transparent;
    }
""")
        
        self.verticalLayout_UserChoose.addWidget(self.listWidget_Users)
        self.horizontalLayout_workarea.addLayout(self.verticalLayout_UserChoose)
        
        # Вторая половина интерфейса
        self.verticalLayout_2half = QtWidgets.QVBoxLayout()
        self.verticalLayout_2half.setObjectName("verticalLayout_2half")
        
        # Время работы, начало и конец
        self.gridLayout_1section = QtWidgets.QGridLayout()
        self.gridLayout_1section.setObjectName("gridLayout_1section")
        
        # Lineedit_timework в котором записывается время работы
        self.gridLayout_1section.addWidget(self.lineEdit_timework, 2, 1, 1, 1)
        self.lineEdit_timework.setStyleSheet("""
QLineEdit {
            border: none;
            background: transparent;
    }
""")
        
        self.label_5 = QtWidgets.QLabel(StaticWidget)
        self.label_5.setObjectName("label_5")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_1section.addWidget(self.label_5, 1, 2, 1, 1)
        
        self.label_4 = QtWidgets.QLabel(StaticWidget)
        self.label_4.setObjectName("label_4")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_1section.addWidget(self.label_4, 1, 1, 1, 1)
        
        #Добавление lineedit начало времени в лэйаут
        self.gridLayout_1section.addWidget(self.dateTimeEdit_Start, 2, 0, 1, 1)
        self.dateTimeEdit_Start.setMinimumWidth(200)
        self.dateTimeEdit_Start.setStyleSheet("""
QLineEdit {
            border: none;
            background: transparent;
    }
""")
        
        # Добавление lineedit конец времени в лэйаут
        self.gridLayout_1section.addWidget(self.dateTimeEdit_End, 2, 2, 1, 1)
        self.dateTimeEdit_End.setMinimumWidth(200)
        self.dateTimeEdit_End.setStyleSheet("""
QLineEdit {
            border: none;
            background: transparent;
    }
""")
        
        self.label_3 = QtWidgets.QLabel(StaticWidget)
        self.label_3.setObjectName("label_3")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_1section.addWidget(self.label_3, 1, 0, 1, 1)
        
        self.verticalLayout_2half.addLayout(self.gridLayout_1section)
        
        # История действий
        self.label_6 = QtWidgets.QLabel(StaticWidget)
        self.label_6.setObjectName("label_6")
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2half.addWidget(self.label_6)

        self.label_count_el.setStyleSheet("""
QLineEdit {
            border: none;
            background: transparent;
    }
""")

        # self.label_count_el.setText(f"Количество добавленных элементов: ")
        
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["Время", "Действие"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setStyleSheet("""
    QTableWidget {
        border: none;
        background: transparent;
    }
    QTableWidget::item {
        background-color: transparent;
    }
    QTableWidget::item:selected {
        color: black;
    }
    QHeaderView::section {
        background-color: transparent;
    }
""")
        
        self.verticalLayout_2half.addWidget(self.tableWidget)
        self.verticalLayout_2half.addWidget(self.label_count_el)
        self.horizontalLayout_workarea.addLayout(self.verticalLayout_2half)
        
        self.gridLayout_2.addLayout(self.horizontalLayout_workarea, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        # #self.lineEdit_timework.setText(self.last_time)
        # self.lineEdit_timework.setText(main_window.get_last_time())  # Получаем время через экземпляр

        # #Таймер

        # # Соединение сигнала с функцией в StaticWidget
        # main_window.time_stopped.connect(self.update_timeworkSW) 

        # #Инициализируем переменные для секундомера
        # self.running = False
        # self.elapsed_time = QTime(0, 0)

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_time)

        #self.start()



        self.retranslateUi(StaticWidget)
        QtCore.QMetaObject.connectSlotsByName(StaticWidget)

    #Ниже 4 функции - реализация работы таймера

    # def start(self):
    #     if not self.running:  # Запускаем таймер, только если он не запущен
    #         self.running = True
    #         self.timer.start(1000)  # Интервал 1000 мс (1 секунда)

    # def stop(self):
    #     if self.running:  # Останавливаем таймер
    #         self.running = False
    #         self.timer.stop()

    # def reset(self):
    #     self.elapsed_time = QTime(0, 0)  # Сбрасываем время
    #     self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    # def update_time(self):
    #     self.elapsed_time = self.elapsed_time.addSecs(1)  # Увеличиваем время на 1 секунду
    #     self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Обновляем отображение времени
    #     self.dateTimeEdit_End.setText(self.elapsed_time.toString("00.00.0000 hh:mm:ss"))

    def get_count_objectS(self, int_):
        self.label_count_el.setText(f"Количество объектов на сцене: {int_}")

    def update_timeworkSW(self, today, new_time, time_now):
        """Слот для приема нового времени и обновления lineEdit_timework."""
        self.lineEdit_timework.setText(new_time)

        from datetime import datetime
        # time_now = datetime.now().strftime("%d.%m.%Y")
        # time_now = datetime.now().strftime("%H:%M:%S")
        # today = datetime.now().strftime("%d.%m.%Y")

        # time_now = QDateTime.fromString(time_now, "HH:mm:ss").time().second()
        # new_time = QDateTime.fromString(new_time, "HH:mm:ss").addMSecs(time_now).toString("HH:mm:ss")

        # time = QTime.fromString(new_time, "hh:mm:ss")
        # if time.isValid():
        #     time = time.addSecs(time_now)
        #     time = time.toString("hh:mm:ss")

        time1 = QDateTime.fromString(time_now, "hh:mm:ss").time()
        time2 = QDateTime.fromString(new_time, "hh:mm:ss").time()

        sum_seconds_time1 = time1.hour() * 3600 + time1.minute() * 60 + time1.second()
        time2 = time2.addSecs(sum_seconds_time1)

        # from datetime import datetime
        date_today = QDateTime.fromString(today, "dd.MM.yyyy").addDays(10).toString("dd.MM.yyyy")

        self.dateTimeEdit_End.setText(f"{date_today} {time2.toString('hh:mm:ss')}")
        print(f"Received : {new_time}")

    def update_last_timeSW(self, today, last_time, time_now):
        self.lineEdit_timework.setText(last_time)

        # time_now = QDateTime.fromString(time_now, "HH:mm:ss").time().second()
        # last_time = QDateTime.fromString(last_time, "HH:mm:ss").addMSecs(time_now).toString("HH:mm:ss")

        from datetime import datetime
        # time_now = datetime.now().strftime("%d.%m.%Y")
        time_now = datetime.now().strftime("%H:%M:%S")

        time1 = QDateTime.fromString(time_now, "hh:mm:ss").time()
        time2 = QDateTime.fromString(last_time, "hh:mm:ss").time()

        sum_seconds_time1 = time1.hour() * 3600 + time1.minute() * 60 + time1.second()
        time2 = time2.addSecs(sum_seconds_time1)

        # from datetime import datetime
        date_today = datetime.now().strftime("%d.%m.%Y")

        self.dateTimeEdit_End.setText(f"{date_today} {time2.toString('hh:mm:ss')}")

        # self.dateTimeEdit_End.setText(f"{today} {last_time}")
        print(f"Received last_time: {last_time}")
        # self.lineEdit_timework.setText(last_time)

    def accept_today(self, today, time_now, last_time):
        self.dateTimeEdit_Start.setText(f"{today} {time_now}")

        self.dateTimeEdit_End.setText(f"{today} {time_now}")

    #Функция для обновления информации на статистике
    def uptade_static(self, username: str, user_id: int, start_work: str, end_work: str, action: str, time_action: str):
        row_position = self.tableWidget.rowCount()
        print(username, user_id, action)
        
        # Добавляем новую строку
        self.tableWidget.insertRow(row_position)
        
        
        # Добавляем данные в ячейки
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(action))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(time_action))

    def retranslateUi(self, StaticWidget):

        # import umleditor
        # from umleditor import last_time


        # Создаём экземпляр MainWindow и вызываем get_last_time()
        # main_window = umleditor.Ui_MainWindow()  # Создаём экземпляр класса Ui_MainWindow


        _translate = QtCore.QCoreApplication.translate
        StaticWidget.setWindowTitle(_translate("StaticWidget", "Статистика"))
        # self.label.setText(_translate("StaticWidget", "Статистика"))
        self.label_2.setText(_translate("StaticWidget", "Пользователь"))
        self.label_3.setText(_translate("StaticWidget", "Начало работы"))
        self.label_4.setText(_translate("StaticWidget", "Время работы"))
        self.label_5.setText(_translate("StaticWidget", "Конец работы"))
        self.label_6.setText(_translate("StaticWidget", "История действий"))
        
        # self.lineEdit_timework.setText("00:00:00")
        # self.dateTimeEdit_Start.setInputMask(_translate("StaticWindow", "00.00.0000 00:00:00"))
        # self.dateTimeEdit_Start.setText(_translate("StaticWindow", "00.00.0000 00:00:00"))
        # self.dateTimeEdit_End.setInputMask(_translate("StaticWindow", "00.00.0000 00:00:00"))
        # self.dateTimeEdit_End.setText(_translate("StaticWindow", "00.00.0000 00:00:00"))

    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    StaticWidget = QtWidgets.QWidget()
    ui = Ui_StaticWidget()
    ui.setupUi(StaticWidget)
    StaticWidget.show()
    sys.exit(app.exec_())