from PySide6.QtWidgets import QApplication
import sys

from stego.gui.main_window import Window


def run():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
