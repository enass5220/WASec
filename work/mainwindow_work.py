'''
    WASec – a software that performs automated tests on websites and scan them for SQL Injection and Cross-site Scripting Vulnerabilites.
    Copyright (c) 2018, Inass Husien.

    WASec is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation, either version 2 of the License or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see <http://www.gnu.org/licenses/>

    You can contact us at e.ismail@it.misuratau.edu.ly
'''
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from robobrowser import browser
from beyondlogin import BeyondLogin
from logindialog_work import Work_LoginDialog
from mainwindow import Ui_MainWindow1
from subwindow_work import Work_SubWindow2
from PyQt5 import QtWidgets, QtGui
from urllib import request


class Work_MainWindow1(QtWidgets.QMainWindow, Ui_MainWindow1):
    after_login = pyqtSignal(dict)

    def __init__(self, parent=None, sender=None):
        super(Work_MainWindow1, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('gui/icon.png'))
        self.btnstart.clicked.connect(self.__begin)
        self.dialog_ui = None
        if sender:
            sender.close()
            self.show()

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
        if len(self.tbloginURL.text()) > 5:
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
        if not self.__empty_fields() and self.__url_good() and not self.dialog_ui:
            self.lblstate.setText("")
            self.info = self.__set_luggage()
            if len(self.tbloginURL.text()) > 0:
                browse = browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
                self.handel = BeyondLogin(browse)
                self.dialog_ui = Work_LoginDialog(self, parent=self)
                self.after_login.connect(self.close_login)
                self.dialog_ui.show()
            else:
                self.are_you_sure()

    def are_you_sure(self):
        choice = QtWidgets.QMessageBox.question(self, "You left the Login URL box empty!",
                                                "Are You sure you don't want to login to the website?\n"
                                                "WASec may need to be authenticated to the website"
                                                " in order to scan them.",
                                                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
        if choice == QtWidgets.QMessageBox.Yes:
            self.info['login_url'] = None
            self.info['logged_in'] = None
            self.close_login(self.info)
        else:
            browse = browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
            self.handel = BeyondLogin(browse)
            self.dialog_ui = Work_LoginDialog(self, parent=self)
            self.after_login.connect(self.close_login)
            self.dialog_ui.show()

    @pyqtSlot(dict)
    def close_login(self, login_info=None):
        if self.dialog_ui:
            self.dialog_ui.close()
        if login_info['login_url']:
            for key in login_info:
                self.info[key] = login_info[key]
        self.ui2 = Work_SubWindow2(win=self, info=self.info)

    def closeEvent(self, event, *args, **kwargs):
        if not self.sender():
            choice = QtWidgets.QMessageBox.question(self, "Exiting",
                                                    "Are You sure you want to exit WASec?",
                                                    QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Yes)
            if choice == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Work_MainWindow1()
    MainWindow.show()
    sys.exit(app.exec_())
