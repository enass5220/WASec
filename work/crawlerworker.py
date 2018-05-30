
from crawler import Spider
from sqliexploiter import SQLiExploiter
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5 import QtCore, QtGui
from time import sleep


class CrawlerWorker(QThread):
    on_info = pyqtSignal(dict)

    def __init__(self, info, instance, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.crawler = Spider(info)
        self.instance = instance
        self.pause = False
        self.on_info.connect(self.populate_tree)

    def run(self):
        self.running = True
        while self.running:
            try:
                i = 0
                while i < 5:
                    print(1)
                    i += 1
                # self.crawler.create_web(self, self)
                self.instance.lblshow_state.setText('Finished crawling.')
                sleep(5)
                self.instance.lblshow_state.setText('Done.')
            except Exception as e:
                print(str(e))

    def populate_tree(self, links):
        data = []
        for index in links:
            item = (links[index]['from'], [])
            for link in links[index]['url']:
                item[1].append((link, []))
            data.append(item)

        model = QtGui.QStandardItemModel()
        self.__add_items(model, data)

        self.instance.treeView.setModel(model)
        self.instance.treeView.expandAll()
        self.instance.treeView.scrollToBottom()

    def __add_items(self, model, data):
        for text, children in data:
            item = QtGui.QStandardItem(text)
            model.appendRow(item)
            if children:
                self.__add_items(item, children)


