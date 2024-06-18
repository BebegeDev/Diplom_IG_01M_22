import sys
import csv
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QPushButton, QMenu, QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, \
    QFrame, QTabWidget, QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QTextBrowser
from PyQt6.QtCore import Qt, pyqtSlot
from input_dialog import InputWidget
from worker import Worker
from main_HPS2 import main_ges
from main_SES import main_ses
from main_ges_ses import main_ges_ses
import Utill.calc as c
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.param_load = None
        self.setWindowTitle("Главное окно")
        self.setGeometry(100, 100, 600, 600)
        self.setFixedSize(1400, 600)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setFixedWidth(800)
        self.splitter.setFixedHeight(500)

        self.button_widget = QWidget()
        self.button_widget.setFixedWidth(400)
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)

        self.button_ges = QPushButton("Открыть окно параметров ГЭС")
        self.button_ges.clicked.connect(self.show_ges_fields)
        self.button_ges.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_ges)

        self.button_ses = QPushButton("Открыть окно параметров СЭС")
        self.button_ses.clicked.connect(self.show_ses_fields)
        self.button_ses.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_ses)

        self.button_load = QPushButton("Открыть окно параметров нагрузки")
        self.button_load.clicked.connect(self.show_load_fields)
        self.button_load.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_load)

        self.button_excel = QPushButton("Загрузить данные из среднемесячных расходов")
        self.button_excel.clicked.connect(self.load_excel_file)
        self.button_excel.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_excel)

        self.button_zf = QPushButton("Загрузка Z_F")
        self.button_zf.clicked.connect(self.load_excel_file_2)
        self.button_zf.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_zf)

        self.button_calculate_ges = QPushButton("Рассчитать ГЭС")
        self.button_calculate_ges.clicked.connect(self.calculate_ges)
        self.button_calculate_ges.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_calculate_ges)

        self.button_calculate_ses = QPushButton("Рассчитать СЭС")
        self.button_calculate_ses.clicked.connect(self.calculate_ses)
        self.button_calculate_ses.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_calculate_ses)

        self.button_calculate_ges_ses = QPushButton("Рассчитать ГЭС+СЭС")
        self.button_calculate_ges_ses.clicked.connect(self.calculate_ges_ses)
        self.button_calculate_ges_ses.setObjectName("rounded_button")
        self.button_layout.addWidget(self.button_calculate_ges_ses)

        self.button_layout.addStretch()

        self.button_widget.setLayout(self.button_layout)
        self.button_widget.setObjectName("button_widget")

        self.fields_widget = QWidget()

        self.splitter.addWidget(self.button_widget)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.splitter.addWidget(line)

        self.splitter.addWidget(self.fields_widget)
        self.text_edit = QTextBrowser()
        self.text_edit.setFixedWidth(700)
        self.splitter.addWidget(self.text_edit)

        self.setCentralWidget(self.splitter)

        self.menu = self.menuBar().addMenu("Файл")
        self.save_as_action = self.menu.addAction("Сохранить как CSV")
        self.save_as_action.triggered.connect(self.save_as_csv)

        self.open_action = self.menu.addAction("Открыть CSV")
        self.open_action.triggered.connect(self.open_csv_file)
        # Создаем экземпляр InputWidget для начального отображения
        initial_input_widget = InputWidget("", [], show_save_button=False)
        self.splitter.replaceWidget(2, initial_input_widget)
        self.saved_data = {}
        self.param_ges = None  # Список для параметров ГЭС
        self.param_ses = None  # Список для параметров СЭС  # Список для параметров нагрузки
        self.zf_data = []  # Список для данных Z_F
        self.param_expenses = []  # Список для данных среднемесячных расходов
        self.workers = []
        self.is_ges_running = False
        self.is_ges_ses_running = False
        self.is_ses_running = False
        self.dialogs = {
            "ГЭС": InputWidget("Параметры ГЭС", ["УНБ", "НПУ", "КПД", "Весенне-летний_период",
                                                 "Осенне–зимний_период", "k_N"
                                                 ]),
            "СЭС": InputWidget("Параметры СЭС", [
                "Локация", "Широта", "Долгота", "ВнУМ", "Год моделирования",
                "Угол наклона к горизонту", "Азимут", "Альбедо", "Площадь СЭС",
                "БД ФЭМ", "БД Инверторов","STC min", "STC max", "Technology", "Bifacial",
                "V_oc_ref_min", "V_oc_ref_max", "Vac", "Paco_min", "Paco_max", "Idcmax", "ka", "kb", "dT"
            ]),
            "Нагрузка": InputWidget("Параметры нагрузки", [
                f"Нагрузка в час {i + 1}" for i in range(24)
            ])
        }

        for dialog in self.dialogs.values():
            dialog.save_data_signal.connect(self.save_data_from_input_widget)

        self.apply_styles()

    @pyqtSlot(dict)
    def save_data_from_input_widget(self, data):
        category = data.pop('category', None)
        if category == "Параметры ГЭС":
            self.param_ges = []
            self.param_ges.append(data)
        elif category == "Параметры СЭС":
            self.param_ses = []
            self.param_ses.append(data)
        elif category == "Параметры нагрузки":
            self.param_load = []
            self.param_load.append(data)
        self.saved_data.update(data)

    def load_data_to_input_widgets(self, data):
        for category, dialog in self.dialogs.items():
            if category in data:
                dialog.load_data(data[category])

    def update_input_widgets(self, data):
        for category, widget in self.dialogs.items():
            if category in data:
                widget.load_data(data[category])

    def apply_styles(self):
        self.setStyleSheet("""
                    QPushButton#rounded_button {
                        border-radius: 10px;
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        transition-duration: 0.4s;
                        cursor: pointer;
                        border: none;
                    }
                    QPushButton#rounded_button:hover {
                        background-color: #45a049;
                    }

                    #button_widget {
                        border: 2px solid #4CAF50;
                        border-radius: 15px;
                        background-color: #f2f2f2;
                        padding: 20px;
                        margin: 20px;
                    }
                """)

    def show_ges_fields(self):
        self.display_fields("ГЭС")

    def show_ses_fields(self):
        self.display_fields("СЭС")

    def show_load_fields(self):
        self.display_fields("Нагрузка")

    def display_fields(self, category):
        widget = self.dialogs.get(category)
        if widget:
            self.splitter.replaceWidget(2, widget)

    def handle_finished(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
            self.text_edit.clear()
            self.text_edit.setHtml(file_content)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл: {str(e)}")

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить скрипт: {error_message}")

    def calculate_ges(self):
        if self.is_ges_running:
            QMessageBox.warning(self, "Предупреждение", "Вычисление ГЭС уже выполняется.")
            return

        self.is_ges_running = True
        worker = Worker(self.run_ges)
        worker.finished.connect(self.handle_finished)
        worker.finished.connect(lambda: self.set_flag('ges', False))
        worker.error.connect(self.handle_error)
        worker.error.connect(lambda: self.set_flag('ges', False))
        self.workers.append(worker)
        worker.start()

    def run_ges(self):
        main_ges(self.q, self.zf_data, self.param_ges)
        return "resources/file/HPS/report_HPS.html"

    def calculate_ges_ses(self):
        if self.is_ges_ses_running:
            QMessageBox.warning(self, "Предупреждение", "Вычисление ГЭС+СЭС уже выполняется.")
            return

        self.is_ges_ses_running = True
        worker = Worker(self.run_ges_ses)
        worker.finished.connect(self.handle_finished)
        worker.finished.connect(lambda: self.set_flag('ges_ses', False))
        worker.error.connect(self.handle_error)
        worker.error.connect(lambda: self.set_flag('ges_ses', False))
        self.workers.append(worker)
        worker.start()

    def run_ges_ses(self):
        main_ges_ses([self.q, self.zf_data, self.param_ges], self.param_ses, self.param_load)
        return "resources/file/HPS_SPP/report_HPS_SPP.html"

    def calculate_ses(self):
        if self.is_ses_running:
            QMessageBox.warning(self, "Предупреждение", "Вычисление СЭС уже выполняется.")
            return

        self.is_ses_running = True
        worker = Worker(self.run_ses)
        worker.finished.connect(self.handle_finished)
        worker.finished.connect(lambda: self.set_flag('ses', False))
        worker.error.connect(self.handle_error)
        worker.error.connect(lambda: self.set_flag('ses', False))
        self.workers.append(worker)
        worker.start()

    def run_ses(self):
        main_ses(self.param_ses)
        return "resources/file/SPP/report_SPP.html"

    def set_flag(self, task, value):
        if task == 'ges':
            self.is_ges_running = value
        elif task == 'ges_ses':
            self.is_ges_ses_running = value
        elif task == 'ses':
            self.is_ses_running = value

    def save_as_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "CSV Files (*.csv)")
            if filename:
                with open(filename, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    for category, dialog in self.dialogs.items():
                        data = [category] + [field.text() for field in dialog.fields.values()]
                        writer.writerow(data)
                QMessageBox.information(self, "Успех", f"Данные сохранены в файле: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def open_csv_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "CSV Files (*.csv)")
            if filename:
                with open(filename, "r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        category = row[0]
                        data = row[1:]
                        if category in self.dialogs:
                            self.dialogs[category].load_data(data)
                QMessageBox.information(self, "Успех", f"Данные загружены из файла: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_excel_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Excel Files (*.xlsx)")
            if filename:
                data = pd.read_excel(filename)
                self.q = c.open_exel(filename)
                formatted_data = pd.melt(data, id_vars="Год", var_name="Месяц", value_name="Значение")
                # Сохраняем данные в param_expenses
                self.param_expenses = formatted_data.to_dict('records')

                years = formatted_data['Год'].unique()

                tab_widget = QTabWidget()
                for year in years:
                    year_data = formatted_data[formatted_data['Год'] == year]

                    # Создаем виджет года
                    year_widget = QWidget()
                    layout = QVBoxLayout()

                    # Создаем метку с информацией о годе
                    year_label = QLabel(f"Данные за {year} год")
                    layout.addWidget(year_label)

                    # Создаем таблицу для отображения данных
                    table_widget = QTableWidget()
                    table_widget.setColumnCount(2)  # Два столбца: "Месяц" и "Значение"
                    table_widget.setRowCount(len(year_data))

                    # Заполняем таблицу данными
                    for i, (index, row) in enumerate(year_data.iterrows()):
                        table_widget.setItem(i, 0, QTableWidgetItem(str(row['Месяц'])))
                        table_widget.setItem(i, 1, QTableWidgetItem(str(row['Значение'])))

                    table_widget.setHorizontalHeaderLabels(["Месяц", "Значение"])
                    layout.addWidget(table_widget)
                    year_widget.setLayout(layout)
                    tab_widget.addTab(year_widget, str(year))
                    table_widget.setObjectName("my_table")

                    # Примените стили с помощью CSS
                    table_widget.setStyleSheet("""
                                #my_table {
                                    border: 2px solid #4CAF50;  /* Рамка таблицы */
                                    border-collapse: collapse;   /* Объединение границ ячеек */
                                    width: 100%;                 /* Ширина таблицы */
                                }
                                #my_table th {
                                    border-bottom: 2px solid #4CAF50;  /* Рамка для заголовков столбцов */
                                    padding: 8px;                        /* Отступ внутри ячейки */
                                    text-align: left;                   /* Выравнивание текста по левому краю */
                                }
                                #my_table td {
                                    border-bottom: 1px solid #ddd;  /* Рамка для данных */
                                    padding: 8px;                    /* Отступ внутри ячейки */
                                    text-align: left;               /* Выравнивание текста по левому краю */
                                }
                            """)
                # self.dialogs["Excel"] = tab_widget
                self.splitter.replaceWidget(2, tab_widget)
                QMessageBox.information(self, "Успех", f"Данные загружены из файла: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_excel_file_2(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Excel Files (*.xlsx)")
            if filename:
                data = pd.read_excel(filename)

                self.zf_data = data

                # Очищаем таблицу, если она уже содержит данные
                table_widget = self.splitter.findChild(QTableWidget)
                if table_widget:
                    table_widget.clear()

                # Создаем новую таблицу
                table_widget = QTableWidget()
                table_widget.setColumnCount(len(data.columns))
                table_widget.setRowCount(len(data))

                # Устанавливаем заголовок таблицы
                table_widget.setHorizontalHeaderLabels(['Z', 'F'])

                # Заполняем таблицу данными
                for row in range(len(data)):
                    for col in range(len(data.columns)):
                        item = QTableWidgetItem(str(data.iloc[row, col]))
                        table_widget.setItem(row, col, item)
                # Добавляем таблицу к splitter
                self.splitter.replaceWidget(2, table_widget)

                QMessageBox.information(self, "Успех", f"Данные загружены из файла: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
