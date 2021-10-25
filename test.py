from sub import *

import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QHeaderView
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton, QMenu

from PyQt5.QtGui import QColor
from threading import Event


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Звонитель 3000')

        # Layouts

        self.main_line = QVBoxLayout(self)
        self.first = QHBoxLayout(self)

        # Button

        self.pushButton = QPushButton(self)
        self.pushButton.setText('Сохранить')
        self.pushButton.clicked.connect(self.save)

        self.menu = QMenu(self)
        self.menu.addAction('Light theme', self.pr)
        self.menu.addAction('Dark theme', self.pr)
        self.status = 'choose'

        self.btn = QPushButton(self)
        self.btn.setMenu(self.menu)
        self.btn.setText('Light theme')

        # Other

        self.all_needed_data = list()
        self.stopFlag = Event()

        # Table

        self.tableWidget = QTableWidget(self)
        self.tableWidget.itemChanged.connect(self.changed)
        self.modified = dict()
        self.titles = None

        # Output

        self.main_line.addWidget(self.btn)
        self.main_line.addWidget(self.tableWidget)
        self.main_line.addWidget(self.pushButton)

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

    def save(self):
        file_work = self.file.cursor()
        res = file_work.execute('''SELECT time, track FROM main_day''').fetchall()
        first = [list(map(lambda x: x[0], res)), list(map(lambda x: x[1], res))]
        self.stopFlag = Event()
        self.thread = MyThread(self.stopFlag, 0.5, first)
        self.thread.start()
        self.pushButton.setEnabled(False)

    def pr(self):
        act = self.sender()
        self.btn.setText(act.text())

        if self.status == 'choose':
            if act.text() == 'Light theme':
                self.status = 'Dark theme'
            else:
                self.status = 'Light theme'

        if act.text() != self.status:
            if self.status == 'Dark theme':
                self.setStyleSheet(f'QWidget {{background-color: "#c4c4c4"}}')
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
                    self.tableWidget.item(i, j).setBackground(QColor(190, 190, 190))
                else:
                    self.tableWidget.item(i, j).setBackground(QColor(130, 130, 130))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = App()
    ex.show()
    sys.exit(app.exec())