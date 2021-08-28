import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.setInterval(1 * 1000)
        self.timer.timeout.connect(self.timeout_run)

    def initUI(self):
        self.btn = QPushButton("Quit", self)
        self.btn.move(300, 60)
        self.btn.resize(self.btn.sizeHint())
        self.btn.clicked.connect(QCoreApplication.instance().quit)

        self.btn1 = QPushButton("Sleep", self)
        self.btn1.move(200, 60)
        self.btn1.resize(self.btn1.sizeHint())
        self.btn1.clicked.connect(self.sleep)
        # 시간을 표시할 라벨 생성
        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 250, 20)
        self.label.move(40, 30)

        self.setWindowTitle("Notifier")
        self.move(300, 300)
        self.resize(400, 100)
        self.show()

    def timeout_run(self):
        self.now = datetime.datetime.now()
        text = self.now.strftime("%Y-%m-%d %H:%M:%S")
        self.label.setText(str(text))

    def sleep(self):
        loop = QEventLoop()
        print("loop start")
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()
        print("loop exit")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
