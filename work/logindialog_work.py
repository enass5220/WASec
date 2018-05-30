from PyQt5 import QtCore, QtGui, QtWidgets
from urllib import request
from exceptions import LoginError, FieldsError
from logindialog import Ui_dialogLogin
import sys


class Work_LoginDialog(QtWidgets.QMainWindow, Ui_dialogLogin):
    def __init__(self, instance=None, parent=None):
        super(Work_LoginDialog, self).__init__(parent)
        self.setupUi(self)
        self.instance = instance

    def go(self):
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.__check_all)
        self.tbloginURL.setText(self.instance.info['login_url'])
        if len(self.tbloginURL.text()) > 5:
            self.tbuser.setFocus()
        self.show()

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
            info = {
                'login_url': self.tbloginURL.text(),
                'user': self.tbuser.text(),
                'pass': self.tbpass.text(),
                'redirect_url': self.tbredirectURL.text()
            }
            try:
                res = self.instance.handel.get_login_info(info)
                if res:
                    print(res)
                    self.hide()
                else:
                    self.lblstate.setText('Login Failed')
            except LoginError:
                self.lblstate.setText('Failed: Wrong Credentials!')
            except FieldsError:
                self.lblstate.setText()
           # finally:
            #    self.instance.check_login()

    def closeEvent(self, event):
        try:
            if self.instance.handel.logged_in:
                #self.instance.check_login()
                event.accept()
            else:
                self.lblstate.setText("not cool")
                event.ignore()
        except Exception:
            #self.instance.running = True
            event.accept()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SubWindow = Work_LoginDialog()
    SubWindow.show()
    sys.exit(app.exec_())