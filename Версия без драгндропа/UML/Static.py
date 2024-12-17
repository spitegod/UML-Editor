import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

class Ui_StaticWidget(QtWidgets.QWidget): 
    def __init__(self):
        super().__init__()

        #Linedit начало времени работы
        self.dateTimeEdit_Start = QtWidgets.QLineEdit(self)
        self.dateTimeEdit_Start.setReadOnly(True)
        self.dateTimeEdit_Start.setInputMask("00.00.0000 00:00:00")
        self.dateTimeEdit_Start.setAlignment(Qt.AlignCenter)
        self.dateTimeEdit_Start.setObjectName("dateTimeEdit_Start")

        #Lineedit в котором записывается время работы
        self.lineEdit_timework = QtWidgets.QLineEdit(self)
        self.lineEdit_timework.setReadOnly(True)
        self.lineEdit_timework.setInputMask("00:00:00")
        self.lineEdit_timework.setAlignment(Qt.AlignCenter)
        self.lineEdit_timework.setObjectName("lineEdit_timework")

        #Lineedit конец времени работы
        self.dateTimeEdit_End = QtWidgets.QLineEdit(self)
        self.dateTimeEdit_End.setReadOnly(True)
        self.dateTimeEdit_End.setInputMask("00.00.0000 00:00:00")
        self.dateTimeEdit_End.setAlignment(Qt.AlignCenter)
        self.dateTimeEdit_End.setObjectName("dateTimeEdit_End")

        #lineeit о количестве объектов на сцене
        self.label_count_el = QtWidgets.QLineEdit(self)
        self.label_count_el.setReadOnly(True)
        self.label_count_el.setAlignment(QtCore.Qt.AlignRight)
        self.label_count_el.setObjectName("label_count_el")

        # Таблица, в которой записывается история действий пользователя
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().hide()

        self.listWidget_Users = QtWidgets.QListWidget(self)
        self.listWidget_Users.setObjectName("listWidget_Users")
        self.listWidget_Users.setFixedWidth(100)

    def setupUi(self, StaticWidget):
        StaticWidget.setObjectName("StaticWidget")
        StaticWidget.setWindowModality(QtCore.Qt.NonModal)
        StaticWidget.setFixedSize(950, 300)  # Фиксируем размер окна

        # Основной layout
        self.gridLayout = QtWidgets.QGridLayout(StaticWidget)
        self.gridLayout.setObjectName("gridLayout")

        # Вложенный layout для рабочего пространства
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")

        # --- Основная рабочая область ---
        self.horizontalLayout_workarea = QtWidgets.QHBoxLayout()
        self.horizontalLayout_workarea.setObjectName("horizontalLayout_workarea")

        # Блок выбора пользователя
        self.verticalLayout_UserChoose = QtWidgets.QVBoxLayout()
        self.verticalLayout_UserChoose.setObjectName("verticalLayout_UserChoose")

        self.label_2 = QtWidgets.QLabel(StaticWidget)
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(Qt.AlignCenter)
        self.verticalLayout_UserChoose.addWidget(self.label_2)

        self.listWidget_Users.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
            }
        """)
        for username in ["User"]:
            item = QtWidgets.QListWidgetItem(username)
            item.setTextAlignment(Qt.AlignCenter)
            self.listWidget_Users.addItem(item)

        self.verticalLayout_UserChoose.addWidget(self.listWidget_Users)
        self.horizontalLayout_workarea.addLayout(self.verticalLayout_UserChoose)

        # Вторая половина интерфейса
        self.verticalLayout_2half = QtWidgets.QVBoxLayout()
        self.verticalLayout_2half.setObjectName("verticalLayout_2half")

        # --- Время работы: начало и конец ---
        self.gridLayout_1section = QtWidgets.QGridLayout()
        self.gridLayout_1section.setObjectName("gridLayout_1section")

        # Метки и поля ввода
        self.label_3 = self.createLabel("label_3", StaticWidget)
        self.gridLayout_1section.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_4 = self.createLabel("label_4", StaticWidget)
        self.gridLayout_1section.addWidget(self.label_4, 1, 1, 1, 1)

        self.label_5 = self.createLabel("label_5", StaticWidget)
        self.gridLayout_1section.addWidget(self.label_5, 1, 2, 1, 1)

        # Поля времени
        self.setStyle(self.dateTimeEdit_Start)
        self.dateTimeEdit_Start.setMinimumWidth(200)
        self.gridLayout_1section.addWidget(self.dateTimeEdit_Start, 2, 0, 1, 1)

        self.setStyle(self.lineEdit_timework)
        self.gridLayout_1section.addWidget(self.lineEdit_timework, 2, 1, 1, 1)

        self.setStyle(self.dateTimeEdit_End)
        self.dateTimeEdit_End.setMinimumWidth(200)
        self.gridLayout_1section.addWidget(self.dateTimeEdit_End, 2, 2, 1, 1)

        self.verticalLayout_2half.addLayout(self.gridLayout_1section)

        # История действий
        self.label_6 = self.createLabel("label_6", StaticWidget)
        self.verticalLayout_2half.addWidget(self.label_6)

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["\u0412\u0440\u0435\u043c\u044f", "\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalLayout_2half.addWidget(self.tableWidget)

        self.setStyle(self.label_count_el)
        self.verticalLayout_2half.addWidget(self.label_count_el)

        self.horizontalLayout_workarea.addLayout(self.verticalLayout_2half)
        self.gridLayout_2.addLayout(self.horizontalLayout_workarea, 1, 0, 1, 1)

        # Добавляем всё в основной layout
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.retranslateUi(StaticWidget)
        QtCore.QMetaObject.connectSlotsByName(StaticWidget)

        self.setDesigh(StaticWidget)

    # Вспомогательные методы для упрощения

    def createLabel(self, name, parent):
        label = QtWidgets.QLabel(parent)
        label.setObjectName(name)
        label.setAlignment(Qt.AlignCenter)
        return label

    def setStyle(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
            }
        """)


    # Отображение количество элементов на сцене
    def get_COUNT_OBJECTS(self, int_):
        self.label_count_el.setText(f"Количество объектов на сцене: {int_}")

    # Слот для приема нового времени и обновления lineEdit_timework.
    def update_timeworkSW(self, today, new_time, time_now):
        self.lineEdit_timework.setText(new_time)
        self.dateTimeEdit_End.setText(f"{today} {time_now}")

    def UPDATE_LAST_TIME_FOR_SW(self, today, last_time, time_now):
        pass

    def accept_today(self, today, time_now, last_time):
        self.dateTimeEdit_Start.setText(f"{today} {time_now}")
        self.dateTimeEdit_End.setText(f"{today} {time_now}")

    #Функция для обновления информации на статистике
    def uptade_static(self, username: str, user_id: int, start_work: str, end_work: str, action: str, time_action: str, action_history):
        if self.listWidget_Users.item(user_id) is None:
            new_item = QtWidgets.QListWidgetItem(username)
            self.listWidget_Users.addItem(new_item)

        self.tableWidget.setRowCount(0)

        # Обновляем текст пользователя
        item = self.listWidget_Users.item(user_id)
        if item:
            item.setText(username)

        # Добавляем строки в таблицу по длине action_history
        for _ in range(len(action_history)):
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

        for row, (time, act) in enumerate(action_history.items()):
            action_item = QTableWidgetItem(act)  # Действие пользователя на сцене
            time_item = QTableWidgetItem(time)  # Время

            # Центрируем содержимое в каждой ячейке
            action_item.setTextAlignment(Qt.AlignCenter)
            time_item.setTextAlignment(Qt.AlignCenter)

            # Устанавливаем элементы в таблицу
            self.tableWidget.setItem(row, 0, action_item)  # Действие
            self.tableWidget.setItem(row, 1, time_item)  # Время

        # Обновляем виджеты
        self.listWidget_Users.update()
        self.tableWidget.update()

    def retranslateUi(self, StaticWidget):
        _translate = QtCore.QCoreApplication.translate
        StaticWidget.setWindowTitle(_translate("StaticWidget", "Статистика"))
        self.label_2.setText(_translate("StaticWidget", "Пользователь"))
        self.label_3.setText(_translate("StaticWidget", "Начало работы"))
        self.label_4.setText(_translate("StaticWidget", "Время работы"))
        self.label_5.setText(_translate("StaticWidget", "Конец работы"))
        self.label_6.setText(_translate("StaticWidget", "История действий"))

    # Применение стилей для окна
    def setDesigh(self, StaticWindow):
        StaticWindow.setWindowIcon(QIcon("imgs/main_icon.png"))
        StaticWindow.setStyleSheet("""
            QWidget {
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                color: #2f2f2f;
                background-color: #f4f4f4;
            }
            QLineEdit {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                background-color: #ffffff;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #76b852;
                background-color: #f1f8e9;
            }
            QLabel {
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #2f2f2f;
            }
            }
            QListWidget {
                border: none;
                background: transparent;
                color: #2f2f2f;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgb(220, 220, 220);
            }
            QTableWidget {
                border-radius: 8px;
                color: #2f2f2f;
                gridline-color: #ddd;
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                border: none;
                background: transparent;
            }

            QTableWidget::item {
                padding: 10px;
                background-color: transparent;
                border-bottom: 1px solid #eee;
            }

            QTableWidget::item:selected {
                background-color: transparent;
                color: black;
            }

            QTableWidget::item:hover {
                background-color: rgba(150, 150, 150, 100);
            }

            QTableWidget::item:selected:hover {
                background-color: rgb(100, 100, 100);
            }

            QHeaderView::section {
                background-color: transparent;
                color: #2f2f2f;
                font-weight: bold;
                border: none;
                padding: 8px;
                border-bottom: 2px solid #2f2f2f;
            }

            QHeaderView::section:horizontal {
                border-right: 1px solid #ccc;
            }

            QHeaderView::section:vertical {
                border-bottom: 1px solid #ccc;
            }

            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #cccccc;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #aaaaaa;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }

            QScrollBar:horizontal {
                border: none;
                background: #f1f1f1;
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal {
                background: #cccccc;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #aaaaaa;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
        """)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    StaticWidget = QtWidgets.QWidget()
    ui = Ui_StaticWidget()
    ui.setupUi(StaticWidget)
    StaticWidget.show()
    sys.exit(app.exec_())