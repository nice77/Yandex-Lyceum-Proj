from sub import *

import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QHeaderView
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QDialog, QDialogButtonBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton, QMenu, QLabel
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QColor
from threading import Event


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Звонителеинатор')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.la = 'Русский'

        # Layouts

        self.main_line = QVBoxLayout(self)
        self.second_line = QHBoxLayout(self)

        # Buttons

        self.add_button = QPushButton(self)
        self.add_button.setText('Добавить строку')
        self.add_button.clicked.connect(self.add_row)

        self.delete_button = QPushButton(self)
        self.delete_button.setText('Удалить строку')
        self.delete_button.clicked.connect(self.delete_row)

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Сохранить')
        self.pushButton.clicked.connect(self.save)

        self.menu = QMenu(self)
        self.menu.addAction('Light theme', self.pr)
        self.menu.addAction('Dark theme', self.pr)
        self.status = 'choose'

        self.menu_1 = QMenu(self)
        self.menu_1.addAction('Русский', self.lang)
        self.menu_1.addAction('English', self.lang)

        self.btn = QPushButton(self)
        self.btn.setMenu(self.menu)
        self.btn.setText('Light theme')

        self.btn_1 = QPushButton(self)
        self.btn_1.setMenu(self.menu_1)
        self.btn_1.setText('Язык')

        self.help_btn = QPushButton(self)
        self.help_btn.setText('Помощь')
        self.help_btn.clicked.connect(self.helper)

        self.buttons = [self.add_button, self.delete_button, self.pushButton, self.help_btn]

        # Other

        self.stopFlag = Event()

        # Table

        self.tableWidget = QTableWidget(self)
        self.tableWidget.itemChanged.connect(self.changed)
        self.modified = dict()
        self.titles = None

        # Output

        self.second_line.addWidget(self.add_button)
        self.second_line.addWidget(self.delete_button)

        self.main_line.addWidget(self.btn)
        self.main_line.addWidget(self.btn_1)
        self.main_line.addWidget(self.tableWidget)
        self.main_line.addWidget(self.pushButton)
        self.main_line.addLayout(self.second_line)
        self.main_line.addWidget(self.help_btn)

        # SQL connections

        self.file = sqlite3.connect("Days.sqlite")
        self.select_data()

    def select_data(self):
        file_work = self.file.cursor()
        res = file_work.execute('''SELECT * FROM main_day''').fetchall()
        self.tableWidget.setColumnCount(len(res[0]))
        self.tableWidget.setRowCount(len(res))
        self.titles = [description[0] for description in file_work.description]

        for i, elem in enumerate(self.titles):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(elem))

        for i, row in enumerate(res):
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.modified = dict()

    def closeEvent(self, event):
        self.file.close()
        self.stopFlag.set()

    def changed(self, item):
        self.modified[self.titles[item.column()]] = [item.text(), item.row() + 1]
        file_work = self.file.cursor()
        que = "UPDATE main_day SET\n"
        que += ", ".join([f"{key}='{self.modified[key][0]}'"for key in self.modified.keys()])
        que += f"WHERE key IN ({', '.join(str(self.modified[i][1]) for i in self.modified.keys())})"
        file_work.execute(que)
        self.file.commit()
        self.modified.clear()
        self.stopFlag.set()
        self.pushButton.setEnabled(True)

    def add_row(self):
        file_work = self.file.cursor()
        que = f'''INSERT INTO main_day
        VALUES ({self.tableWidget.rowCount() + 1}, '00:00', 'txt')'''
        file_work.execute(que)
        self.file.commit()
        self.select_data()

    def delete_row(self):
        file_work = self.file.cursor()
        que = f'''DELETE FROM main_day WHERE key = {self.tableWidget.rowCount()}'''
        file_work.execute(que)
        self.file.commit()
        self.select_data()

    def save(self):
        file_work = self.file.cursor()
        res = file_work.execute('''SELECT time, track FROM main_day''').fetchall()
        first = [list(map(lambda x: x[0], res)), list(map(lambda x: x[1], res))]
        self.stopFlag = Event()
        self.thread = MyThread(self.stopFlag, 60, first)
        self.thread.start()
        self.pushButton.setEnabled(False)

    def pr(self):
        act = self.sender()
        if self.la == 'Русский':
            if act.text() == 'Light theme':
                self.btn.setText('Светлая тема')
            else:
                self.btn.setText('Тёмная тема')
        else:
            self.btn.setText(act.text())

        if self.status == 'choose':
            if act.text() == 'Light theme':
                self.status = 'Dark theme'
            else:
                self.status = 'Light theme'

        if act.text() != self.status:
            if self.status == 'Dark theme':
                self.setStyleSheet(f'QWidget {{background-color: "#ffffff"}}')
                self.status = 'Light theme'
            else:
                self.setStyleSheet(f'QWidget {{background-color: "#707070"}}')
                self.status = 'Dark theme'
            self.table_color(self.status)
            print(act.text(), self.status)

    def table_color(self, val):
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                if val == 'Light theme':
                    self.tableWidget.item(i, j).setBackground(QColor(250, 250, 250))
                else:
                    self.tableWidget.item(i, j).setBackground(QColor(130, 130, 130))

    def lang(self):
        self.la = self.sender().text()
        self.btn_1.setText(self.la)
        di_to_ru = {'Help': 'Помощь', 'Save': 'Сохранить',
                    'Delete row': 'Удалить строку',
                    'Write row': 'Добавить строку'}
        di_to_eng = {'Помощь': 'Help', 'Сохранить': 'Save',
                     'Удалить строку': 'Delete row',
                     'Добавить строку': 'Write row'}
        print(self.help_btn.text())
        if self.la == 'Русский' and self.help_btn.text() != 'Помощь':
            for i in self.buttons:
                i.setText(di_to_ru[i.text()])
            self.setWindowTitle('Callinator')
        elif self.la == 'English' and self.help_btn.text() != 'Help':
            for i in self.buttons:
                i.setText(di_to_eng[i.text()])
            self.setWindowTitle('Звонителеинатор')

    def helper(self):
        msg = HelpWindow()
        msg.exec()
        if msg.accepted:
            msg.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            dlg = CustomDialog(self.la)
            if dlg.exec():
                self.close()


class CustomDialog(QDialog):
    def __init__(self, lang):
        super().__init__()
        if lang == 'English':
            self.setWindowTitle('Exit')
            message = QLabel("Do you want to exit from callinator?")
        else:
            self.setWindowTitle('Выход')
            message = QLabel("Выйти из звонителеинатора?")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class HelpWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Справка')
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.main_line = QVBoxLayout(self)

        self.lab = QLabel(self)
        self.lab.setText(open('assets/info.txt', encoding='utf-8').read())
        self.main_line.addWidget(self.lab)
        self.setLayout(self.main_line)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App()
    ex.show()
    sys.exit(app.exec())
