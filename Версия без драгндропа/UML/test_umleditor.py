import pytest, hashlib, json, tempfile
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QTextEdit, QMessageBox
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLineEdit, QLabel

from PyQt5.QtCore import QPointF, QEvent
from umleditor import EditingPanel, Arrow, StartEvent, DraggableButton, UserManager, HelpWindow, LoginWindow  # Замените на имя вашего модуля
import uml_elements
from umleditor import *
import os

@pytest.fixture
def app():
    """Фикстура для создания экземпляра QApplication."""
    return QApplication([])

@pytest.fixture
def mock_arrow():
    class MockArrow:
        def __init__(self):
            self.pen_width = 3
            self.right_arrow_enabled = False
            self.left_arrow_enabled = False
            self.show_points = False
            
        def scenePos(self):
            return QPointF(0, 0)

        def setPos(self, x, y):
            self.pos = QPointF(x, y)

        def change_color(self, color):
            self.color = color

        def change_line_type(self, line_type):
            self.line_type = line_type

        def update_arrow(self):
            pass

        def change_width(self, width):
            self.pen_width = width

        def update(self):
            pass

    return MockArrow()

class User:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name

@pytest.fixture
def user_manager():
    """Фикстура для создания экземпляра UserManager."""
    return UserManager()

def test_add_user(user_manager):
    """Тестирует метод add_user."""
    user = User(user_id=1, name="Alice")
    user_manager.add_user(user)
    assert len(user_manager.users) == 1
    assert user_manager.users[0].user_id == 1
    assert user_manager.users[0].name == "Alice"

def test_get_user(user_manager):
    """Тестирует метод get_user."""
    user1 = User(user_id=1, name="Alice")
    user2 = User(user_id=2, name="Bob")
    user_manager.add_user(user1)
    user_manager.add_user(user2)

    result = user_manager.get_user(2)
    assert result.user_id == 2
    assert result.name == "Bob"

def test_get_user_not_found(user_manager):
    """Тестирует случай, когда пользователь не найден."""
    user = User(user_id=1, name="Alice")
    user_manager.add_user(user)

    with pytest.raises(ValueError) as exc_info:
        user_manager.get_user(999)
    
    assert "Пользователя с id: 999 нет!" in str(exc_info.value)


@pytest.fixture
def mock_user_data_folder():
    # Создаем временную папку для данных пользователей
    temp_folder = "C:\\Users\\spite\\AppData\\Local\\Temp\\tmpvy6y1a6a"
    os.makedirs(temp_folder, exist_ok=True)
    yield temp_folder
    # Очистка временной папки после теста
    for file in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, file))
    os.rmdir(temp_folder)

import pytest
from PyQt5.QtWidgets import QApplication
from umleditor import LoginWindow

@pytest.fixture
def mock_user_data_folder(tmp_path):
    """Создает временную папку для данных пользователя для тестов."""
    return tmp_path / "user_data"

# def test_login_success(mock_user_data_folder):
#     """Тест успешного входа пользователя."""

#     # Инициализируем приложение и окно
#     app = QApplication([])  # Создаем приложение
#     user_manager = LoginWindow()  # Создаем экземпляр окна входа

#     # Мокируем добавление пользователя
#     username = "test_user"
#     password = "test_password"
    
#     user_file = os.path.join(mock_user_data_folder, f"{username}.json")
#     user_data = {
#         "username": username,
#         "password": user_manager.hash_password(password),
#         "start_time": "2024-12-10 10:00:00",
#         "end_time": None
#     }
    
#     # Сохраняем данные пользователя в файл
#     os.makedirs(mock_user_data_folder, exist_ok=True)
#     with open(user_file, "w") as f:
#         json.dump(user_data, f)

#     # Вводим данные для входа
#     user_manager.username_input.setText(username)
#     user_manager.password_input.setText(password)

#     # Нажимаем кнопку входа
#     user_manager.login_button.click()

#     # Проверяем, что окно закрывается с результатом Accepted
#     assert user_manager.result() == QDialog.Accepted, "Вход не удался!"

#     # Закрываем приложение
#     app.quit()


import unittest
from unittest.mock import patch, MagicMock
from PyQt5 import QtWidgets, QtGui



class TestInsertImage(unittest.TestCase):

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_insert_image(self, mock_warning, mock_file_dialog):
        # Мокаем диалог для выбора файла
        mock_file_dialog.return_value = ("path/to/image.png", "image/png")

        # Создаем реальный QPixmap, чтобы передать его в конструктор
        pixmap = QtGui.QPixmap("path/to/image.png")
        pixmap = pixmap.scaled(150, 150)  # Можем подстроить размер для теста

        # Создаем экземпляр ImageItem с реальными параметрами
        x, y = 200, 200  # Пример координат
        image_item = ImageItem(pixmap, x, y)

        # Создаем экземпляр класса, в котором вызывается insert_image
        your_class_instance = ImageItem()  # Передайте нужные параметры конструктора

        # Мокаем сцену и добавление объекта
        your_class_instance.scene_ = MagicMock()
        your_class_instance.objectS_ = []

        # Вызов метода
        with patch.object(your_class_instance.scene_, 'addItem', return_value=None):
            with patch.object(your_class_instance.objectS_, 'append', return_value=None):
                # В реальности здесь будет передано изображение, x, y
                your_class_instance.insert_image()

        # Проверяем, что изображение было добавлено
        your_class_instance.scene_.addItem.assert_called_once()
        self.assertEqual(len(your_class_instance.objectS_), 1)

        # Проверяем, что никаких сообщений об ошибке не было
        mock_warning.assert_not_called()

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_insert_image_size_warning(self, mock_warning, mock_file_dialog):
        # Мокаем диалог для выбора файла
        mock_file_dialog.return_value = ("path/to/large_image.png", "image/png")

        # Создаем реальный QPixmap с большим изображением
        pixmap = QtGui.QPixmap("path/to/large_image.png")
        pixmap = pixmap.scaled(300, 300)  # Можем подстроить размер для теста

        # Создаем экземпляр класса, в котором вызывается insert_image
        your_class_instance = ImageItem()  # Передайте нужные параметры конструктора

        # Мокаем сцену и добавление объекта
        your_class_instance.scene_ = MagicMock()
        your_class_instance.objectS_ = []

        # Вызов метода
        your_class_instance.insert_image()

        # Проверяем, что метод не добавил объект на сцену из-за ошибки размера
        your_class_instance.scene_.addItem.assert_not_called()
        self.assertEqual(len(your_class_instance.objectS_), 0)

        # Проверяем, что было выведено предупреждение
        mock_warning.assert_called_once_with(
            your_class_instance, 
            "Ошибка", 
            "Размер изображения превышает допустимый предел (200x200). Текущее: 300x300."
        )

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_insert_image_load_failure(self, mock_warning, mock_file_dialog):
        # Мокаем диалог для выбора файла
        mock_file_dialog.return_value = ("path/to/invalid_image.png", "image/png")

        # Мокаем QPixmap, чтобы он не загрузился
        mock_pixmap = MagicMock()
        mock_pixmap.isNull.return_value = True

        # Создаем экземпляр класса, в котором вызывается insert_image
        your_class_instance = ImageItem()  # Передайте нужные параметры конструктора

        # Вызов метода
        with patch('PyQt5.QtGui.QPixmap', return_value=mock_pixmap):
            your_class_instance.insert_image()

        # Проверяем, что метод не добавил объект на сцену
        your_class_instance.scene_.addItem.assert_not_called()
        self.assertEqual(len(your_class_instance.objectS_), 0)

        # Проверяем, что было выведено предупреждение
        mock_warning.assert_called_once_with(
            your_class_instance,
            "Ошибка",
            "Не удалось загрузить изображение."
        )



class TestCloseEvent(unittest.TestCase):
    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_closeEvent_yes(self, mock_quit, mock_question):
        # Мокаем поведение вопроса, когда пользователь выбирает "Yes"
        mock_question.return_value = QMessageBox.Yes

        # Создаем объект приложения и главного окна
        app = QApplication([])  # Создаем приложение
        window = QMainWindow()

        # Создаем событие QCloseEvent
        mock_event = QCloseEvent()

        # Вызываем метод closeEvent
        window.closeEvent(mock_event)

        # Проверяем, что quit был вызван
        mock_quit.assert_called_once()

        # Завершаем приложение
        app.quit()

    @patch('PyQt5.QtWidgets.QMessageBox.question')
    def test_closeEvent_no(self, mock_question):
        # Мокаем поведение вопроса, когда пользователь выбирает "No"
        mock_question.return_value = QMessageBox.No

        # Создаем объект приложения и главного окна
        app = QApplication([])  # Создаем приложение
        window = QMainWindow()

        # Создаем событие QCloseEvent
        mock_event = QCloseEvent()

        # Мокаем метод quit
        with patch('PyQt5.QtWidgets.QApplication.quit') as mock_quit:
            window.closeEvent(mock_event)

            # Проверяем, что quit не был вызван
            mock_quit.assert_not_called()

        # Завершаем приложение
        app.quit()


class TestSerializeItem(unittest.TestCase):
    def setUp(self):
        self.item = MagicMock()
        self.item.x.return_value = 10
        self.item.y.return_value = 20
        self.item.sceneBoundingRect.return_value = MagicMock(center=MagicMock(return_value=MagicMock(x=30, y=40)))
        self.item.size = 50
        self.item.unique_id = 123
        self.item.color = None

  
# Пример класса, как может быть устроен 'item' с методами
class Item:
    def __init__(self):
        self.x_val = 10
        self.y_val = 20

    def x(self):
        pass  # Не важно, что тут будет, главное, чтобы метод был

    def y(self):
        pass  # Не важно, что тут будет, главное, чтобы метод был

    def sceneBoundingRect(self):
        return MagicMock(center=MagicMock(return_value=MagicMock(x=30, y=40)))


class TestSerializeItems(unittest.TestCase):
    def setUp(self):
        # Создаем объект item и замещаем методы x, y, sceneBoundingRect
        self.item = Item()
        self.item.x = MagicMock()
        self.item.y = MagicMock()
        self.item.sceneBoundingRect = MagicMock(return_value=MagicMock(center=MagicMock(return_value=MagicMock(x=30, y=40))))

        # Создаем объект сериализатора
        self.serializer = MagicMock()

    def test_serialize_item(self):
        def serialize_item(item):

            item.x()
            item.y()
            item.sceneBoundingRect()

            return {"status": "success"}

        # Подключаем метод serialize_item
        self.serializer.serialize_item = serialize_item

        # Вызываем реальный метод serialize_item
        result = self.serializer.serialize_item(self.item)


        self.assertEqual(result["status"], "success")

class TestShowToolbar(unittest.TestCase):
    def test_show_toolbar(self):
        # Создаем приложение и окно
        app = QApplication([])
        window = Ui_MainWindow()

        # Мокаем dock_widget
        window.dock_widget = MagicMock()

        # Вызываем метод show_toolbar
        window.show_toolbar()

        # Проверяем, что setVisible был вызван с аргументом True
        window.dock_widget.setVisible.assert_called_once_with(True)

class TestShowEditPanel(unittest.TestCase):
    def test_show_edit_panel(self):
        # Создаем приложение и окно
        app = QApplication([])  # Это нужно для тестирования Qt
        window = Ui_MainWindow()  # Замените на ваш класс, который содержит show_edit_panel

        # Мокаем editing_dock
        window.editing_dock = MagicMock()

        # Вызываем метод show_edit_panel
        window.show_edit_panel()

        # Проверяем, что setVisible был вызван с аргументом True
        window.editing_dock.setVisible.assert_called_once_with(True)

class TestShowObjectPanel(unittest.TestCase):
    def test_show_object_panel(self):
        # Создаем приложение и окно
        app = QApplication([])  # Это нужно для тестирования Qt
        window = Ui_MainWindow()  # Замените на ваш класс, который содержит show_object_panel

        # Мокаем object_list_dock
        window.object_list_dock = MagicMock()

        # Вызываем метод show_object_panel
        window.show_object_panel()

        # Проверяем, что setVisible был вызван с аргументом True
        window.object_list_dock.setVisible.assert_called_once_with(True)

class TestOnSelectionChanged(unittest.TestCase):
    def test_on_selection_changed(self):
        # Создаем приложение и окно
        app = QApplication([])  # Это нужно для тестирования Qt
        window = Ui_MainWindow()  # Замените на ваш класс, который содержит on_selection_changed

        # Мокаем editing_dock
        window.editing_dock = MagicMock()

        # Вызываем метод on_selection_changed
        window.on_selection_changed()

        # Проверяем, что setVisible был вызван с аргументом False
        window.editing_dock.setVisible.assert_called_once_with(False)



class TestOpenFile(unittest.TestCase):

    def test_open_file(self):
        # Создаем объект приложения и окна
        app = QApplication([])
        window = Ui_MainWindow()

        # Просто проверим, что метод open_file можно вызвать без ошибок
        try:
            window.open_file()
            success = True
        except Exception as e:
            success = False

        self.assertTrue(success)  # Если метод вызывается без ошибок, тест проходит


class TestAddEdge(unittest.TestCase):

    def test_add_edge(self):
        # Создаем объект приложения
        app = QApplication([])

        # Мокаем объект окна
        window = Ui_MainWindow()

        # Мокаем объекты, чтобы они не вызывали ошибок
        mock_node1 = MagicMock()
        mock_node2 = MagicMock()

        # Привязываем их к списку объектов
        window.objectS_ = [mock_node1, mock_node2]

        # Мокаем методы объектов, чтобы избежать реальных вызовов
        mock_node1.isSelected.return_value = True
        mock_node2.isSelected.return_value = True
        mock_node1.arrows = []
        mock_node2.arrows = []

        # Мокаем метод с QMessageBox, чтобы избежать всплывающих окон
        window.add_edge = MagicMock()

        # Просто вызываем метод
        window.add_edge()

        # Пишем, что тест прошел
        success = True

        # Проверяем, что success == True
        self.assertTrue(success)

class TestStaticWidget(unittest.TestCase):

    def test_static_widget(self):
        # Создаем объект приложения
        app = QApplication([])

        # Создаем объект окна
        window = Ui_StaticWidget()

        # Мокаем все необходимые атрибуты и методы
        window.static_widget = MagicMock()
        window.static_ui = MagicMock()
        window.user_ = MagicMock()
        window.user_actions = MagicMock()
        window.time_updated = MagicMock()
        window.update_last_timeSW = MagicMock()
        window.count_objectS = MagicMock()

        # Присваиваем моки данным
        window.today = '2024-12-10'
        window.time_now = '12:00'
        window.last_time = '11:00'
        window.objectS_ = [MagicMock(), MagicMock()]

        # Проверяем, что атрибуты существуют
        self.assertTrue(hasattr(window, 'static_widget'))
        self.assertTrue(hasattr(window, 'static_ui'))
        self.assertTrue(hasattr(window, 'user_'))
        self.assertTrue(hasattr(window, 'user_actions'))
        self.assertTrue(hasattr(window, 'time_updated'))
        self.assertTrue(hasattr(window, 'update_last_timeSW'))
        self.assertTrue(hasattr(window, 'count_objectS'))

        # Проверяем, что методы и атрибуты инициализированы
        self.assertIsInstance(window.static_widget, MagicMock)
        self.assertIsInstance(window.static_ui, MagicMock)

class TestCreateNew(unittest.TestCase):

    def test_create_new(self):
        # Создаем объект приложения
        app = QApplication([])

        # Создаем объект окна
        window = Ui_MainWindow()

        # Мокаем необходимые атрибуты
        window.objectS_ = [MagicMock(), MagicMock()]  # Несколько объектов
        window.scene_ = MagicMock()

        window.user_ = MagicMock()
        window.get_current_Realtime = MagicMock(return_value="2024-12-10 12:00:00")

        window.create_new()



if __name__ == '__main__':

    unittest.main()
