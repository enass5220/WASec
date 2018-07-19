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
from xml.etree import cElementTree as cET
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime


class Reporter:

    def __init__(self, log=False, info=None, items=None, window=None):
        self.log = log
        self.__info__ = info
        self.__items__ = items
        self.window = window

    def saver(self):
        dlg = QFileDialog()
        dlg.setWindowIcon(self.window.windowIcon())
        options = QFileDialog.options(dlg)
        options |= QFileDialog.DontUseNativeDialog
        dlg.setOption(dlg.DontConfirmOverwrite, False)
        filename = QFileDialog.getSaveFileName(dlg, '', '', 'Text Documents (*.txt);;XML Documents (*.xml)',
                                               ".txt", options=options)  # type: tuple
        if filename[0]:  # if a file name has been supplied (i.e. user entered a name)
            try:
                if '.xml' in filename[1]:
                    res = self.write_xml(filename[0])
                else:
                    res = self.write_txt(filename[0])  # writes txt files
                return res
            except Exception as e:
                return str(e)
        else:
            return 'canceled'

    @staticmethod
    def __header__(head):
        if head == 'crawl':
            header = ['ID', 'FROM', 'URL']
        else:
            header = ['INDEX', 'URL', 'TYPE', 'PAYLOAD']
        return header

    def write_xml(self, filename):
        try:
            root = cET.Element('WASec')
            info = cET.SubElement(root, 'scan-info', time=datetime.now().time().isoformat(),
                                  date=datetime.now().date().isoformat())
            cET.SubElement(info, 'base-url').text = self.__info__['base_url']
            cET.SubElement(info, 'robots.txt').text = self.__info__['robo_url']
            cET.SubElement(info, 'max-crawl').text = self.__info__['max_crawl']
            cET.SubElement(info, 'login-url').text = self.__info__['login_url']
            cET.SubElement(info, 'scan-option').text = self.__info__['option']
            cET.SubElement(info, 'time-taken').text = self.__info__['time']

            if 'crawl' in self.__items__:
                crawl = cET.SubElement(root, 'Crawling-Results',
                                       found=str(self.__items__['crawl']['total']),
                                       crawled=str(self.__items__['crawl']['total_crawled']),
                                       invalid=str(self.__items__['crawl']['invalid']),
                                       took=self.__items__['crawl']['time'])
                for index in self.__items__['crawl']['links']:
                    fro = cET.SubElement(crawl, 'from', index=str(index),
                                         parent=self.__items__['crawl']['links'][index]['from'])
                    i = 0
                    for url in self.__items__['crawl']['links'][index]['url'].keys():
                        cET.SubElement(fro, 'url-' + str(i + 1),
                                       title=self.__items__['crawl']['links'][index]['url'][url]).text = url
                        i += 1
            if 'sql' in self.__items__:
                sql = cET.SubElement(root, 'SQLi-Results')
                ssql = cET.SubElement(sql, 'Exploited-Links',
                                      total=str(self.__items__['sql']['count']),
                                      took=self.__items__['sql']['time'])
                for index in self.__items__['sql']['exploited']:
                    sub = cET.SubElement(ssql, 'Link', index=str(index))
                    cET.SubElement(sub, 'URL').text = self.__items__['sql']['exploited'][index]['url']
                    cET.SubElement(sub, 'Type').text = self.__items__['sql']['exploited'][index]['type']
                    cET.SubElement(sub, 'Payload').text = self.__items__['sql']['exploited'][index]['payload']
                faults = cET.SubElement(sql, 'Faults')
                i = 1
                for f in self.__items__['sql']['faults']:
                    fault = cET.SubElement(faults, 'fault', index=str(i))
                    cET.SubElement(fault, 'url').text = str(f['url'])
                    cET.SubElement(fault, 'error').text = str(f['fault'])
                    i += 1

            if 'xss' in self.__items__:
                xss = cET.SubElement(root, 'XSS-Results')
                xxss = cET.SubElement(xss, 'Exploited-Links',
                                      total=str(self.__items__['xss']['count']),
                                      took=self.__items__['xss']['time'])
                for index in self.__items__['xss']['exploited']:
                    sub = cET.SubElement(xxss, 'Link', index=str(index))
                    cET.SubElement(sub, 'URL').text = self.__items__['xss']['exploited'][index]['url']
                    cET.SubElement(sub, 'Type').text = self.__items__['xss']['exploited'][index]['type']
                    cET.SubElement(sub, 'Payload').text = self.__items__['xss']['exploited'][index]['payload']
                faults = cET.SubElement(xss, 'Faults')
                i = 1
                for f in self.__items__['xss']['faults']:
                    fault = cET.SubElement(faults, 'fault', index=str(i))
                    cET.SubElement(fault, 'url').text = str(f['url'])
                    cET.SubElement(fault, 'error').text = str(f['fault'])
                    i += 1

            tree = cET.ElementTree(root)
            tree.write(str(filename) + '.xml')
            return None
        except Exception as e:
            return str(e)

    def write_txt(self, filename):
        try:
            with open(str(filename) + '.txt', 'x') as file:
                file.write('WASEC SCAN\n___________________\n')
                file.write('Date: ' + datetime.now().date().isoformat())
                file.write('\nTime: ' + datetime.now().time().isoformat())
                file.write('\n___________________\n')
                file.write('Base URL: ' + str(self.__info__['base_url']))
                file.write('\nRobots.txt: '+str(self.__info__['robo_url']))
                file.write('\nMax-Crawl: '+str(self.__info__['max_crawl']))
                file.write('\nLogin URL: '+str(self.__info__['login_url']))
                file.write('\nScan Option: '+str(self.__info__['option']))
                file.write('\nTime Taken: '+self.__info__['time'])

                if 'crawl' in self.__items__:
                    file.write('\n________________________\n')
                    file.write(
                        '- CRAWLED URLS ( found: '+str(self.__items__['crawl']['total'])
                        + ' links, crawled: '+str(self.__items__['crawl']['total_crawled'])
                        + ' links, invalid: '+str(self.__items__['crawl']['invalid'])
                        + ' links, time taken: '+self.__info__['time']+')\n')

                    header = self.__header__('crawl')
                    for index in self.__items__['crawl']['links']:
                        file.write(header[0] + ': ' + str(index + 1) + '\n')
                        file.write(header[1] + ': ' + str(self.__items__['crawl']['links'][index]['from']) + '\n')
                        file.write(header[2] + ':\n')
                        for url in self.__items__['crawl']['links'][index]['url'].keys():
                            file.write('- Title: '+self.__items__['crawl']['links'][index]['url'][url]+'  ==>  '+str(url)+'\n')
                    file.write('\n')

                if 'sql' in self.__items__:
                    file.write('\n________________________\n')
                    file.write('- SQL Injection Testing ( found ' + str(self.__items__['sql']['count'])
                               + ' vulnerable pages, time taken: '+self.__items__['sql']['time']+' )\n')
                    header = self.__header__('sql')
                    for index in self.__items__['sql']['exploited']:
                        file.write(header[0] + ': ' + str(index + 1) + '\n')
                        file.write(header[1] + ': ' + str(self.__items__['sql']['exploited'][index]['url']) + '\n')
                        file.write(header[2] + ': ' + str(self.__items__['sql']['exploited'][index]['type']) + '\n')
                        file.write(header[3] + ': ' + str(self.__items__['sql']['exploited'][index]['payload']) + '\n')
                    file.write('\n')
                    i = 1
                    for fault in self.__items__['sql']['faults']:
                        file.write('\n* Errors Occurred:\n')
                        file.write(str(i)+')\n- Page: '+str(fault['url']))
                        file.write('\n- Error: ' + str(fault['fault']))
                        i += 1
                    file.write('\n')

                if 'xss' in self.__items__:
                    file.write('\n________________________\n')
                    file.write('- Cross-site Scripting Testing ( found ' + str(self.__items__['xss']['count'])
                               + ' vulnerable pages, time taken: '+self.__items__['xss']['time']+' )\n')
                    header = self.__header__('xss')
                    for index in self.__items__['xss']['exploited']:
                        file.write(header[0] + ': ' + str(index + 1) + '\n')
                        file.write(header[1] + ': ' + str(self.__items__['xss']['exploited'][index]['url']) + '\n')
                        file.write(header[2] + ': ' + str(self.__items__['xss']['exploited'][index]['type']) + '\n')
                        file.write(header[3] + ': ' + str(self.__items__['xss']['exploited'][index]['payload']) + '\n')
                    file.write('\n')
                    i = 1
                    for fault in self.__items__['xss']['faults']:
                        file.write('\n* Errors Occurred:\n')
                        file.write(str(i)+')\n- Page: '+str(fault['url']))
                        file.write('\n- Error: ' + str(fault['fault']))
                        i += 1
                    file.write('\n')
                file.close()
                return None
        except Exception as e:
            return str(e)
