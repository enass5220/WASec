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

from PyQt5 import QtWidgets
from urllib import request
from PyQt5.QtCore import pyqtSignal
from exceptions import LoginError, FieldsError
from logindialog import Ui_dialogLogin


class Work_LoginDialog(QtWidgets.QMainWindow, Ui_dialogLogin):

    logged_in = pyqtSignal()
    close_window = pyqtSignal()

    def __init__(self, win=None, parent=None):
        super(Work_LoginDialog, self).__init__(parent)
        self.setupUi(self)
        self.parent_win = win
        self.buttonBox.rejected.connect(self.are_you_sure)
        self.buttonBox.accepted.connect(self.__check_all)
        self.tbloginURL.setText(self.parent_win.info['login_url'])
        if len(self.tbloginURL.text()) > 5:
            self.tbuser.setFocus()

    def __empty_fields(self):
        if self.tbloginURL.text() != "" and self.tbredirectURL.text() and self.tbpass.text() != "" and self.tbuser.text() != "" :
            return False
        self.lblstate.setText("Please fill all fields")
        return True

    def __url_good(self):
        try:
            request.urlopen(self.tbloginURL.text())
            return True
        except Exception:
            self.lblstate.setText("Invalid URL!")
        return False

    def __check_all(self):
        if not self.__empty_fields()and self.__url_good():
            self.info = {
                'login_url': self.tbloginURL.text(),
                'user': self.tbuser.text(),
                'pass': self.tbpass.text(),
                'redirect_url': self.tbredirectURL.text(),
                'logged_in': False
            }
            try:
                res = self.parent_win.handel.get_login_info(self.info)
                if res:
                    self.info['logged_in'] = True
                    self.parent_win.after_login.emit(self.info)
                else:
                    self.lblstate.setText('Login Failed')
            except LoginError:
                self.lblstate.setText('Login failed!')
            except FieldsError:
                self.lblstate.setText('Invalid Fields Were Found!')

    def closeEvent(self, event, *args, **kwargs):
        if not self.sender():
            choice = QtWidgets.QMessageBox.question(self, "Login", "Are you sure you want to cancel logging in?\n"
                                                                   "Some parts of the website may need WASec to be "
                                                                   "authenticated to be able to scan them.",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def are_you_sure(self):
        choice = QtWidgets.QMessageBox.question(self, "Login", "Are you sure you want to cancel logging in?\n"
                                                            "Some parts of the website may need WASec to be "
                                                            "authenticated to be able to scan them.",
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.info = {
                'login_url': None,
                'logged_in': False
            }
            self.parent_win.after_login.emit(self.info)
        else:
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SubWindow = Work_LoginDialog()
    SubWindow.show()
    sys.exit(app.exec_())
