import sys

import pydirectinput
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator
import keyboard


class ClickerThread(QThread):

    def __init__(self, interval, parent=None):
        super().__init__(parent)
        self.interval = interval / 1000
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            print('clicked')
            pydirectinput.click(button='left')
            pydirectinput.PAUSE = self.interval

    def stop(self):
        self.running = False
        print('stopped')


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.auto = False
        self.buttons()
        keyboard.add_hotkey('f6', self.toggle_clicker)

    def initUI(self):
        uic.loadUi('autoclickerUI.ui', self)
        self.stopButton.setEnabled(False)
        self.intervalEdit.setValidator(QIntValidator())
        self.intervalEdit.setText('100')
        self.setWindowTitle('AutoClicker')

    def buttons(self):
        self.startButton.clicked.connect(self.toggle_clicker)
        self.stopButton.clicked.connect(self.toggle_clicker)

    def toggle_clicker(self):
        if self.auto:
            self.stop()
        else:
            self.start()

    def start(self):
        try:
            self.auto = True

            self.clicker_thread = ClickerThread(float(self.intervalEdit.text()))
            self.clicker_thread.start()

            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)

        except ValueError:
            self.startButton.setEnabled(True)
            print('valueerror')

    def stop(self):
        self.auto = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.clicker_thread.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Widget()
    window.show()
    app.exec()
