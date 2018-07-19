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
import threading
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from reporter import Reporter
from sqliexploiter import SQLiExploiter
from crawlerworker import CrawlerWorker
from subwindow import Ui_MainWindow2
import time
from datetime import datetime, timedelta
from xssexploiter import XSSExploiter


class Work_SubWindow2(QtWidgets.QMainWindow, Ui_MainWindow2):
    change_state = pyqtSignal(str)
    on_info = pyqtSignal(dict)
    show_total = pyqtSignal(int)
    next = pyqtSignal()
    crawl_finished = pyqtSignal(dict)

    def __init__(self, win=None, info=None, parent=None):
        super(Work_SubWindow2, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('gui/icon.png'))
        if info['option'] != 'crawl' and info['max_crawl'] == 1:
            option = 'Testing one page!'
            self.next.connect(self.sqli_tab)

        elif info['option'] == 'sql':
            self.next.connect(self.sqli_tab)
            self.tabxss.setHidden(True)
            option = 'Testing for SQL Injection (SQLi)'

        elif info['option'] == 'xss':
            self.next.connect(self.xss_tab)
            self.tabsqli.setHidden(True)
            option = 'Testing for Cross-site Scripting (XSS)'

        elif info['option'] == 'crawl':
            self.next.connect(self.report_tab)
            self.tabxss.setHidden(True)
            self.tabsqli.setHidden(True)
            option = 'Crawl Only'
        else:
            self.next.connect(self.sqli_tab)
            option = 'Full Testing (SQLi + XSS)'

        self.setWindowTitle("WASec: " + option)
        self.lbloption.setText(option)
        self.btnnew.clicked.connect(self.new_scan)
        self.btnExit.clicked.connect(self.exiting)
        self.btnsave.clicked.connect(self.save_report)
        self.win = win
        self.info = info
        if 'logged_in' not in self.info:
            self.info['logged_in'] = None
        self.result = {}
        self.crawled = {}
        self.show()
        self.win.close()
        self.saved = False
        self.time = datetime.now().time()
        self.crawler = CrawlerWorker(self.info, self)
        self.tab_crawl()

    def tab_crawl(self):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabcrawl))
        self.lbltarget.setText(self.info['base_url'])
        self.change_state.connect(self.on_status_change)
        self.on_info.connect(self.populate_tree)
        self.show_total.connect(self.show_total_links)
        self.crawl_finished.connect(self.__after_crawling)
        self.show()
        self.win.hide()
        self.change_state.emit('Crawling...')
        self.crawling = threading.Thread(target=self.crawler.run, daemon=True)
        self.crawling.start()

    def on_status_change(self, msg):
        self.lblshow_state.setText(msg)

    def show_total_links(self, total):
        self.lbltotallinks.setText('Found ' + str(total) + ' Links')

    def populate_tree(self, links):
        data = []
        for index in links:
            item = (links[index]['from'], [])  # parent link
            for link in links[index]['url'].keys():  # child link
                item[1].append((link, []))
            data.append(item)

        model = QtGui.QStandardItemModel()
        self.__add_items(model, data)

        self.treeView.setModel(model)
        self.treeView.expandAll()
        self.treeView.scrollToBottom()

    def __add_items(self, model, data):
        for text, children in data:
            item = QtGui.QStandardItem(text)
            model.appendRow(item)
            if children:
                self.__add_items(item, children)

    def __after_crawling(self, results):
        self.result['crawl'] = results
        if results['running']:
            self.next.emit()
        else:
            self.lblshow_state.setText('Canceling...')
            time.sleep(2)
            self.report_tab()

    def sqli_tab(self):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabsqli))
        self.lblsqltot.setText('Found 0 vulnerable pages')
        self.pbsqltotal.setMaximum(self.result['crawl']['total_crawled'])
        self.sql_exploiter = SQLiExploiter(self.result['crawl'], self.info, self)
        threading.Thread(target=self.sql_exploiter.run, daemon=True).start()

    def after_sqli(self, results):
        self.result['sql'] = results
        if results['running']:
            if self.info['option'] == 'full':
                self.xss_tab()
            else:
                self.report_tab()
        else:
            self.lblsqltot.setText('Canceling...')
            self.report_tab()

    def xss_tab(self):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabxss))
        self.lblxsstot.setText('Found 0 vulnerable pages')
        self.pbxsstotal.setMaximum(self.result['crawl']['total'])
        self.xss_exploiter = XSSExploiter(self.result['crawl'], self.info, self)
        threading.Thread(target=self.xss_exploiter.run, daemon=True).start()

    def after_xss(self, results):
        self.result['xss'] = results
        if results['running']:
            time.sleep(3)
            self.report_tab()
        else:
            self.lblsqltot.setText('Canceling...')
            time.sleep(3)
            self.report_tab()

    def report_tab(self):
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabreport))
        self.get_time()
        self.lbltotalpages.setText(str(self.result['crawl']['total']))
        if self.info['option'] == 'xss':
            self.gbxss.setFixedHeight(self.gbxss.height() + 135)
            self.listxss.setFixedHeight(self.listxss.height() + 135)
            self.gbxss.setGeometry(self.gbsqli.geometry())
            self.lbldisx.setGeometry(QtCore.QRect(0, 120, 41, 21 + 265))
            self.lbltx.setGeometry(QtCore.QRect(40, 120, 191, 21 + 265))
            self.gbsqli.setHidden(True)

        elif self.info['option'] == 'sql':
            self.gbxss.setHidden(True)
            self.gbsqli.setFixedHeight(self.gbsqli.height() + 135)
            self.listsqli.setFixedHeight(self.listsqli.height() + 135)
            self.lbldisq.setGeometry(QtCore.QRect(0, 120, 41, 21 + 265))
            self.lbltq.setGeometry(QtCore.QRect(40, 120, 191, 21 + 265))

        elif self.info['option'] == 'crawl':
            self.gbxss.setHidden(True)
            self.gbsqli.setFixedHeight(self.gbsqli.height() + 135)
            self.listsqli.setFixedHeight(self.listsqli.height() + 135)
            self.lbldisq.setHidden(True)
            self.lbltq.setHidden(True)
            self.gbsqli.setTitle("Crawling Results")
        self.populate()
        pass

    def populate(self):
        if (self.info['option'] == 'sql') and (self.info['option'] in self.result):

            for index in self.result['sql']['exploited']:
                self.listsqli.addItem(str(index+1) + "- " + self.result['sql']['exploited'][index]['url'])
            self.lbltq.setText(str(self.result['sql']['count']))
            percent = round((self.result['sql']['count'] / self.result['crawl']['total_crawled']) * 100, 2)
            self.lblwvp.setText(str(percent) + '%')

        elif (self.info['option'] == 'xss') and (self.info['option'] in self.result):
            for index in self.result['xss']['exploited']:
                self.listxss.addItem(str(index+1) + "- " + self.result['xss']['exploited'][index]['url'])
            self.lbltx.setText(str(self.result['xss']['count']))
            percent = round((self.result['xss']['count'] / self.result['crawl']['total_crawled']) * 100, 2)
            self.lblwvp.setText(str(percent) + '%')

        elif self.info['option'] == 'full':
            for index in self.result['xss']['exploited']:
                self.listxss.addItem(str(index+1) + "- " + self.result['xss']['exploited'][index]['url'])
            self.lbltx.setText(str(self.result['xss']['count']))

            for index in self.result['sql']['exploited']:
                self.listsqli.addItem(str(index+1) + "- " + self.result['sql']['exploited'][index]['url'])
            self.lbltq.setText(str(self.result['sql']['count']))

            count = 0
            for index in self.result['xss']['exploited']:
                for i in self.result['sql']['exploited']:
                    if self.result['sql']['exploited'][i]['url'] == self.result['xss']['exploited'][index]['url']:
                        count += 1
            percent = round((((self.result['sql']['count'] + self.result['xss']['count']) - count) / self.result['crawl'][
                'total_crawled']) * 100, 2)
            self.lblwvp.setText(str(percent) + '%')

        elif (self.info['option'] == 'crawl') and (self.info['option'] in self.result):
            for index in self.result['crawl']['links']:
                i = 1
                for link in self.result['crawl']['links'][index]['url']:
                    self.listsqli.addItem(str(i) + "- " + link)
                    i += 1
            self.lblwvp.setText('0%')
            self.lbltq.setText('No vulnerable pages')

    def get_time(self):
        finish = datetime.now().time()
        delta1 = timedelta(seconds=self.time.second, microseconds=self.time.microsecond,
                           minutes=self.time.minute, hours=self.time.hour)
        delta2 = timedelta(seconds=finish.second, microseconds=finish.microsecond,
                           minutes=finish.minute, hours=finish.hour)
        taken = delta2 - delta1
        seconds = round(taken.total_seconds())
        if seconds >= 3600:
            hours = round(seconds / 3600)
            minutes = (round((seconds / 3600) / 60))
            elapsed = str(hours)+':'+str(minutes)+' hrs'
        elif seconds >= 60:
            minutes = round(seconds / 60)
            seconds = round(seconds % 60)
            elapsed = str(str(minutes)+'.'+str(seconds)+' mins')
        elif seconds < 0:
            hours = round(seconds / 3600)
            minutes = (round((seconds / 3600) / 60))
            hours = 24+hours
            elapsed = str(hours) + ':' + str(minutes) + ' hrs'
        else:
            elapsed = str(seconds)+' secs'
        self.info['time'] = elapsed
        self.lbltotaltime.setText(elapsed)

    def new_scan(self):
        from mainwindow_work import Work_MainWindow1
        if not self.saved:
            choice = QMessageBox.question(self, "New Scan",
                                          "You haven't saved your last test result.\n"
                                          "Do you still want to start a new scan?",
                                          QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.ui1 = Work_MainWindow1(sender=self)
        else:
            self.ui1 = Work_MainWindow1(sender=self)

    def save_report(self):
        report = Reporter(self.info['option'], self.info, self.result, self)
        result = report.saver()
        msg = QMessageBox()
        msg.setWindowIcon(self.windowIcon())
        msg.setWindowTitle("WASec | Save Report")
        if not result:
            self.saved = True
            msg.setIcon(QMessageBox.Information)
            msg.setText('Your Report Was Saved Successfully!')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif result == 'canceled':
            pass
        else:
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Error occurred while saving report!\n' + result)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def exiting(self):
        choice = QMessageBox.question(self, "Exiting",
                                      "Are You sure you want to exit WASec?",
                                      QMessageBox.Cancel | QMessageBox.Ok)
        if choice == QMessageBox.Ok:
            self.close()

    def closeEvent(self, event, *args, **kwargs):
        if not self.sender():
            choice = QMessageBox.question(self, "Exiting",
                                          "Are You sure you want to exit WASec?",
                                          QMessageBox.Cancel | QMessageBox.Yes)
            if choice == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    SubWindow = Work_SubWindow2()
    SubWindow.show()
    sys.exit(app.exec_())
