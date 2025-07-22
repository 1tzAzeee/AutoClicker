import sys

from assets.generatedUI.main_widget import Ui_MainWidget
from assets.generatedUI.hotkey_widget import Ui_HotkeyWidget
import pydirectinput
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QFile, QTextStream
from PyQt6.QtGui import QIntValidator
import keyboard
import pynput


class HotkeyRecorder(QThread):
    hotkey_recorded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.keys_pressed = []

    def run(self):
        def on_press(key):
            try:
                key_str = key.char
                if '_l' in key_str or '_r' in key_str:
                    key_str = key_str[:-2]
            except AttributeError:
                key_str = str(key).replace("Key.", "")
                if '_l' in key_str or '_r' in key_str:
                    key_str = key_str[:-2]

            if key_str not in self.keys_pressed:
                self.keys_pressed.append(key_str)
            return True

        def on_release(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key).replace("Key.", "")

            if key_str in self.keys_pressed:
                self.hotkey_recorded.emit('+'.join(self.keys_pressed))
                print('+'.join(self.keys_pressed))
                self.keys_pressed.clear()
                return False

        with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


class KeyListenerThread(QThread):
    key_pressed = pyqtSignal(str)

    def run(self):
        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key).replace("Key.", "")
            self.key_pressed.emit(key_str)
            return False

        with pynput.keyboard.Listener(on_press=on_press) as listener:
            listener.join()


class ClickerThread(QThread):

    def __init__(self, clickType, clickMode, repeatMode, button, repeatCount=0, milliseconds=0, seconds=0, parent=None,
                 parentWidget=None):
        super().__init__(parent)
        self.interval = milliseconds / 1000 + seconds
        self.running = False
        self.clickType = clickType
        self.repeatMode = repeatMode
        self.clickButton = button
        self.repeatCount = repeatCount
        self.clickMode = clickMode
        self.parentWidget = parentWidget

    def run(self):
        self.running = True
        while self.running:
            if self.clickMode == 'Mouse':
                if self.repeatMode == 'RepeatUntilStopped':
                    if self.clickType == 'Single':
                        pydirectinput.click(button=self.clickButton.lower())
                        pydirectinput.PAUSE = self.interval
                    if self.clickType == 'Double':
                        pydirectinput.doubleClick(button=self.clickButton.lower())
                        pydirectinput.PAUSE = self.interval
                    if self.clickType == 'Triple':
                        pydirectinput.tripleClick(button=self.clickButton.lower())
                        pydirectinput.PAUSE = self.interval
                    print('clicked')
                else:
                    for i in range(self.repeatCount):
                        if not self.running:
                            break
                        if self.clickType == 'Single':
                            pydirectinput.click(button=self.clickButton.lower())
                            pydirectinput.PAUSE = self.interval
                        if self.clickType == 'Double':
                            pydirectinput.doubleClick(button=self.clickButton.lower())
                            pydirectinput.PAUSE = self.interval
                        if self.clickType == 'Triple':
                            pydirectinput.tripleClick(button=self.clickButton.lower())
                            pydirectinput.PAUSE = self.interval
                    else:
                        self.parentWidget.stop()
            else:
                if self.repeatMode == 'RepeatUntilStopped':
                    pydirectinput.press(self.clickButton.lower())
                    pydirectinput.PAUSE = self.interval
                else:
                    for i in range(self.repeatCount):
                        if not self.running:
                            break
                        pydirectinput.press(self.clickButton.lower())
                        pydirectinput.PAUSE = self.interval
                    else:
                        self.parentWidget.stop()

    def stop(self):
        self.running = False


class MainWidget(QWidget, Ui_MainWidget):
    def __init__(self):
        super().__init__()
        self.hotkey = 'F6'
        self.hotkeyForm = HotkeyWidget(self)
        self.hotkeyForm.hide()
        self.initUI()
        self.hotkeys()
        self.auto = False

    def hotkeys(self):
        keyboard.add_hotkey(self.hotkey, self.toggle_clicker)

    def initUI(self):
        self.setupUi(self)
        self.setFixedSize(401, 383)
        self.buttons()
        self.stopButton.setEnabled(False)
        self.intervalEdit1.setValidator(QIntValidator())
        self.intervalEdit1.setText('100')
        self.intervalEdit2.setValidator(QIntValidator())
        self.setWindowTitle('AutoClicker')
        self.mouseModeToggle.setChecked(True)
        self.repeatUntilStoppedToggle.setChecked(True)
        self.repeatSpinBox.setValue(1)

    def buttons(self):
        self.startButton.clicked.connect(self.toggle_clicker)
        self.stopButton.clicked.connect(self.toggle_clicker)
        self.setKeyButton.clicked.connect(self.startKeyCapture)
        self.hotkeyButton.clicked.connect(self.openForm)
        self.hotkeyForm.data_sent.connect(self.hotkeyChange)

    def toggle_clicker(self):
        if self.auto:
            self.stop()
        else:
            self.start()

    def start(self):
        try:
            self.auto = True

            clickType = self.clickTypeComboBox.currentText()

            clickMode = 'Mouse' if self.mouseModeToggle.isChecked() else 'Keyboard'

            repeatMode = 'RepeatUntilStopped' if self.repeatUntilStoppedToggle.isChecked() else 'Repeat'

            clickButton = self.mouseButtonsBox.currentText() if clickMode == 'Mouse' else self.keyLabel.text()

            repeatCount = self.repeatSpinBox.value()

            millisecs = int(self.intervalEdit1.text()) if self.intervalEdit1.text() else 0
            secs = int(self.intervalEdit2.text()) if self.intervalEdit2.text() else 0

            if millisecs == 0 and secs == 0:
                millisecs = 100
                self.intervalEdit1.setText('100')

            self.clicker_thread = ClickerThread(clickType, clickMode, repeatMode, clickButton, repeatCount,
                                                milliseconds=millisecs, seconds=secs, parentWidget=self)
            self.clicker_thread.start()

            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)

        except ValueError:
            self.startButton.setEnabled(True)

    def stop(self):
        self.auto = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.clicker_thread.stop()

    def startKeyCapture(self):
        self.setKeyButton.setEnabled(False)

        self.listener_thread = KeyListenerThread()
        self.listener_thread.key_pressed.connect(self.updateKey)
        self.listener_thread.start()

    def updateKey(self, key):
        self.current_key = key
        self.setKeyButton.setEnabled(True)
        self.keyLabel.setText(key.upper())

    def openForm(self):
        if self.hotkeyForm.isVisible():
            if self.hotkeyForm.isMinimized():
                self.hotkeyForm.showNormal()
            self.hotkeyForm.raise_()
            self.hotkeyForm.activateWindow()
        else:
            self.hotkeyForm.show()

    def hotkeyChange(self, keys):
        try:
            self.hotkey = keys
            self.hotkeys()
            self.hotkeyForm.hotkeyLabel.setText(keys)
        except Exception as e:
            print(e.__class__.__name__)
            self.hotkeyForm.setHotkeyButton.setEnabled(True)

    def closeEvent(self, a0):
        if self.hotkeyForm.isVisible():
            self.hotkeyForm.close()


class HotkeyWidget(QWidget, Ui_HotkeyWidget):
    data_sent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(300, 100)
        self.parent = parent
        self.setHotkeyButton.clicked.connect(self.startKeyCapture)

    def startKeyCapture(self):
        self.setHotkeyButton.setEnabled(False)

        self.hotkey_thread = HotkeyRecorder()
        self.hotkey_thread.hotkey_recorded.connect(self.updateKey)
        self.hotkey_thread.start()

    def updateKey(self, key):
        self.data_sent.emit(key)
        self.setHotkeyButton.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWidget()
    window.show()
    app.exec()
