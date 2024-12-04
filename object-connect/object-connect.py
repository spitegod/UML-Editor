import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtCore import Qt, QRect


class ResizableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.resizing = False
        self.setReadOnly(True)  # Поле изначально только для чтения
        self.setPlaceholderText("Дважды кликните для редактирования")
        self.setStyleSheet("border: 1px dashed black;")  # Пунктирная рамка

        self.resize_handle_size = 10  # Размер области для изменения размеров

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_in_resize_zone(event.pos()):
                self.resizing = True
                self.start_resize_pos = event.globalPos()  # Глобальная позиция курсора
                self.start_geometry = self.geometry()  # Текущая геометрия
            else:
                self.dragging = True
                self.offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            self._resize(event.globalPos())  # Используем глобальную позицию для расчета изменения
        elif self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
        else:
            self._update_cursor(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Включение редактирования текста по двойному клику
        if self.isReadOnly():
            self.setReadOnly(False)
            self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        # Завершение редактирования текста при потере фокуса
        self.setReadOnly(True)
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        # Ограничение длины текста до 250 символов
        if len(self.toPlainText()) >= 250 and event.key() not in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right):
            return
        super().keyPressEvent(event)

    def adjustSizeToContent(self):
        # Получаем размеры содержимого текста
        text_rect = self.document().documentLayout().blockBoundingRect(self.document().lastBlock())

        # Устанавливаем минимальный размер, чтобы поле корректно отображалось
        width = max(int(text_rect.width()), 100)
        height = max(int(text_rect.height()), 40)

        self.setFixedSize(width + 10, height + 10)

    def _is_in_resize_zone(self, pos):
        """Проверяет, находится ли курсор в зоне изменения размера (нижний правый угол)."""
        rect = self.rect()
        return rect.width() - self.resize_handle_size <= pos.x() <= rect.width() and \
               rect.height() - self.resize_handle_size <= pos.y() <= rect.height()

    def _resize(self, global_pos):
        """Изменяет размеры текстового поля."""
        dx = global_pos.x() - self.start_resize_pos.x()
        dy = global_pos.y() - self.start_resize_pos.y()

        new_width = max(self.start_geometry.width() + dx, 100)  # Минимальная ширина
        new_height = max(self.start_geometry.height() + dy, 40)  # Минимальная высота

        self.setGeometry(self.start_geometry.x(), self.start_geometry.y(), new_width, new_height)

    def _update_cursor(self, pos):
        """Обновляет вид курсора в зависимости от позиции."""
        if self._is_in_resize_zone(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Текстовое поле с изменением размеров")
        self.setGeometry(100, 100, 800, 600)

        # Добавляем текстовое поле
        self.text_edit = ResizableTextEdit(self)
        self.text_edit.move(100, 100)  # Начальная позиция


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())