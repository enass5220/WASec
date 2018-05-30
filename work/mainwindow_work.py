from mainwindow import Ui_MainWindow1
from subwindow_work import Work_SubWindow2
from PyQt5 import QtCore, QtGui, QtWidgets
from urllib import request


class Work_MainWindow1(QtWidgets.QMainWindow, Ui_MainWindow1):
    def __init__(self, parent= None):
        super(Work_MainWindow1, self).__init__(parent)
        self.setupUi(self)
        self.btnstart.clicked.connect(self.__begin)

    def __empty_fields(self):
        if self.tbbaseURL.text() != "":
            if self.rbcrawl.isChecked() or self.rbfull.isChecked() or self.rbsql.isChecked() or self.rbxss.isChecked():
                return False
        self.lblstate.setText("Please fill all fields")
        return True

    def __url_good(self):
        if len(self.tbrobURL.text()) > 5:
            try:
                request.urlopen(self.tbrobURL.text())
            except Exception:
                self.lblstate.setText("Invalid Robots.txt URL!")
                return False

        try:
            request.urlopen(self.tbloginURL.text())
        except Exception:
            self.lblstate.setText("Invalid Website URL!")
            return False

        try:
            request.urlopen(self.tbbaseURL.text())
            return True
        except Exception:
            self.lblstate.setText("Invalid Website URL!")
            return False

    def __set_luggage(self):
        main = {
            'base_url': self.tbbaseURL.text(),
            'robo_url': self.tbrobURL.text(),
            'max_crawl': self.sbmaxcrawl.value(),
            'login_url': self.tbloginURL.text()
        }
        if self.rbxss.isChecked():
            main['option'] = 'xss'
        elif self.rbsql.isChecked():
            main['option'] = 'sql'
        elif self.rbfull.isChecked():
            main['option'] = 'full'
        elif self.rbcrawl.isChecked():
            main['option'] = 'crawl'
        return main

    def __begin(self):
        if not self.__empty_fields() and self.__url_good():
            luggage = self.__set_luggage()
            self.window2 = QtWidgets.QMainWindow()
            try:
                self.ui2 = Work_SubWindow2(win=self, info=luggage)
            except Exception as e:
                print(str(e))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Work_MainWindow1()
    MainWindow.show()
    sys.exit(app.exec_())
