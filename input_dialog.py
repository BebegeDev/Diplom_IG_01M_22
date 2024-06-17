from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt


class InputWidget(QWidget):
    save_data_signal = pyqtSignal(dict)
    calculate_signal = pyqtSignal()  # Новый сигнал для кнопки "Рассчитать"

    def __init__(self, title, field_labels, show_save_button=True):
        super().__init__()

        self.layout = QVBoxLayout()
        self.title = title
        # Добавляем заголовок
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: green")  # Изменяем цвет текста на зеленый
        self.layout.addWidget(self.title_label)

        # Создаем виджет прокручиваемой области
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Позволяет виджету изменять размер в соответствии с содержимым
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_layout = QVBoxLayout(scroll_widget)  # Создаем макет внутри виджета прокручиваемой области

        # Добавляем поля ввода в макет прокручиваемой области
        self.fields = {}
        self.labels = {}
        for label in field_labels:
            line_edit = QLineEdit()
            self.fields[label] = line_edit
            label_widget = QLabel(label)
            self.labels[label] = label_widget
            label_widget.setStyleSheet("color: green")  # Изменяем цвет текста на зеленый
            scroll_layout.addWidget(label_widget)  # Добавляем виджет метки в макет прокручиваемой области
            scroll_layout.addWidget(line_edit)  # Добавляем виджет поля ввода в макет прокручиваемой области

        # Устанавливаем стиль прокручиваемой области
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #f0f0f0; /* Цвет фона */
                border: 1px solid #c0c0c0; /* Обводка */
                border-radius: 5px; /* Закругление углов */
            }
            QScrollBar:vertical {
                width: 8px; /* Ширина вертикальной прокрутки */
                background-color: #e0e0e0; /* Цвет фона */
                margin: 0px 0px 0px 0px; /* Внешние отступы */
                border-radius: 4px; /* Закругление углов */
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0; /* Цвет ползунка */
                min-height: 20px; /* Минимальная высота ползунка */
                border-radius: 4px; /* Закругление углов */
            }
            QScrollBar::add-line:vertical {
                height: 0px; /* Высота кнопки увеличения */
            }
            QScrollBar::sub-line:vertical {
                height: 0px; /* Высота кнопки уменьшения */
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: none; /* Нет фона для области страницы */
            }
        """)

        # Добавляем макет прокручиваемой области в основной макет
        self.layout.addWidget(scroll_area)
        if show_save_button:
            # Добавляем кнопку сохранения в основной макет
            self.save_button = QPushButton("Сохранить")
            self.save_button.clicked.connect(self.save_data)
            self.layout.addWidget(self.save_button)
        

        
        
        self.setLayout(self.layout)

        # Устанавливаем максимальный размер виджета
        # self.setMaximumSize(400, 400)  # Измените размеры по вашему усмотрению

    def save_data(self):
        data = {}
        incomplete = False

        # Проверяем заполненность всех полей
        for label, field in self.fields.items():
            if not field.text():
                incomplete = True
                # Выделяем незаполненное поле и метку
                field.setStyleSheet("background-color: rgba(255, 0, 0, 0.2);")
                self.labels[label].setStyleSheet("color: red;")
                if not self.labels[label].text().endswith("*"):
                    self.labels[label].setText(self.labels[label].text() + " *")
            else:
                data[label] = field.text()
                field.setStyleSheet("")
                self.labels[label].setStyleSheet("color: green;")
                if self.labels[label].text().endswith("*"):
                    self.labels[label].setText(self.labels[label].text()[:-2])

        if incomplete:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля перед сохранением!")
            return

        data['category'] = self.title  # Добавляем категорию в данные
        self.save_data_signal.emit(data)
        QMessageBox.information(self, "Успех", "Данные сохранены!")

    def calculate(self):
        self.calculate_signal.emit()

    def load_data(self, data):
        if isinstance(data, list):  # Проверяем, является ли data списком
            for field, value in zip(self.fields.values(),
                                    data):  # Используем zip для параллельного перебора полей и значений
                field.setText(str(value))  # Устанавливаем значение поля, преобразуем в строку
        elif isinstance(data, dict):  # Добавим обработку словаря
            for label, value in data.items():
                if label in self.fields:
                    self.fields[label].setText(str(value))





