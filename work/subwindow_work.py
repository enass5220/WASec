from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from robobrowser import browser
from beyondlogin import BeyondLogin
from crawler import CrawlerWorker
from logindialog_work import Work_LoginDialog
from subwindow import Ui_MainWindow2
from time import sleep


class Work_SubWindow2(QtWidgets.QMainWindow, Ui_MainWindow2):
    change_state = pyqtSignal(str)

    def __init__(self, parent=None, win=None, info=None):
        super(Work_SubWindow2, self).__init__(parent)
        self.setupUi(self)
        self.win = win
        self.info = info
        self.crawler_thread = CrawlerWorker(self.info, self)
        self.change_state.connect(self.on_status_change)
        self.show()
        self.startme()

    def on_status_change(self, msg):
        self.lblshow_state.setText(msg)

    def startme(self):
        self.win.hide()
        self.change_state.emit('Crawling...')
        ###
        self.window = QtWidgets.QDialog()
        browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
        self.handel = BeyondLogin(browser, self.info['login_url'])
        self.ui = Work_LoginDialog(self, parent=self)
        self.ui.go()

        #self.crawler_thread.start()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SubWindow = Work_SubWindow2()
    SubWindow.show()
    sys.exit(app.exec_())
