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
from urllib import parse
from time import sleep
from robobrowser import browser  # Helps generating requests for webpages
from robotexclusionrulesparser import RobotExclusionRulesParser
from PyQt5.QtCore import QObject
from beyondlogin import BeyondLogin
from requests import exceptions
import urllib3
from datetime import datetime, timedelta


class CrawlerWorker(QObject):  # spider that will get links of website # called to create instance of the class
    finish = False

    def __init__(self, info, instance, parent=None):
        super(CrawlerWorker, self).__init__(parent)
        self._instance = instance
        self.running = True
        self.base_url = info['base_url']  # main url of website
        self._links_to_crawl = []  # list of links yet to open
        self.crawled_links = {}  # dictionary of links opened/all links
        self.__parsed_crawled = {}  # list of urls and their html pages
        self.total = 0  # total number of found links
        self.total_crawled = 0  # total number of valid crawled links in website
        self.max_pages = info['max_crawl']  # max pages to crawl
        self.invalid_links_count = 0  # number of broken links found
        self.invalid_links_list = []  # list of broken links found
        self.dynamic = []
        self.info = info
        self.login_url = info['login_url']  # login page url if available
        if info['robo_url']:
            self._rb_parser = RobotExclusionRulesParser()
            self._rb_parser.fetch(info['robo_url'])
            self._user_agent = 'WASecBot'
        else:
            self._rb_parser = None
        self.browser = browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
        self.browser.session.verify = False
        self._logged_in = False
        self.running = True
        self._instance.btncrawlcancel.clicked.connect(self.pause)
        self._elapsed = 0
        self.delay = 15
        self._requests = 0
        self.start = None
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _opener(self, url):
        retry = 1
        while True:
            try:
                self.browser.open(url=url)
                break
            except exceptions.ConnectionError as ce:
                sleep(self.delay * retry)
                if retry == 11:
                    return False
                else:
                    retry += 1
        return True

    def _compute_crawl_delay(self):
        self._requests += 1
        if self._requests <= 10:
            self._elapsed += self.browser.response.elapsed.total_seconds()
            delay = self._elapsed / self._requests
            self.delay = delay * 200
            if self.delay >= 180:
                self.delay = 15
        else:
            self._requests = 1
            self._elapsed = self.browser.response.elapsed.total_seconds()
            self.delay = self._elapsed * 200

    def pause(self):
        self.running = False
        self._instance.change_state.emit('Canceling...')
        choice = QtWidgets.QMessageBox.question(self._instance, "Cancel Crawl!",
                                                "WASec is not finished yet, are You sure you want to stop crawling?",
                                                QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Yes)
        if choice == QtWidgets.QMessageBox.Yes:
            self.finish = True
            self.running = False
            self._instance.crawl_finished.emit(self._wrap_up())
        else:
            self.running = True

    # get total number of links opened so far
    def total_links(self):
        total = 0
        for index in self.crawled_links:
            total += len(self.crawled_links[index]['url'])
        return total

    # check if max pages reached
    def _crawled_max(self):
        result = (self.max_pages == 0) or (self.max_pages > self.total_links())
        return result

    # is link already listed
    def _is_link_listed(self, link):
        self._instance.change_state.emit('Check if URL is listed...')
        url = parse.urljoin(self.base_url, link)
        result = False
        for index in self.crawled_links:
            for opened in self.crawled_links[index]['url'].keys():
                if url == opened or link == opened:
                    result = True
        for to_open in self._links_to_crawl:
            if link == to_open[1] or url == to_open[1]:
                result = True
        return result

    # gets dynamic urls
    def _is_dynamic(self, url):
        self._instance.change_state.emit('Check if URL is dynamic...')
        if '?' in str(url) or '=' in str(url):
            self.dynamic.append(url)

    # check if page opened and exists
    def _is_response_ok(self, url):
        # status_code 200 means OK; no problems with page
        if 200 == self.browser.response.status_code:
            return True
        else:
            self._instance.change_state.emit('URL is invalid!')
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            return False

    def _is_html_page(self, url):
        try:
            if 'text/html' in self.browser.response.headers["content-type"]:
                return True
            else:
                self.invalid_links_count += 1
                self.invalid_links_list.append(url)
                self._instance.change_state.emit('URL is invalid!')
                return False
        except KeyError:
            return True

    def _is_same_page(self, url):
        if self.browser.url != url:
            res = self._opener(url)
        else:
            res = True
        if res:
            page = self.browser.parsed
            for index in self.crawled_links:
                for link in self.crawled_links[index]['url'].keys():
                    check = self.__parsed_crawled[link]
                    if check == page:
                        self._instance.change_state.emit('URL is invalid!')
                        return False
            return True
        else:
            self.finish = True
            self.running = False
            return False

    def _page_wise(self, url):
        if self.browser.url != url:
            res = self._opener(url)
        else:
            res = True
        if res:
            return self._is_response_ok(url) and self._is_html_page(url) and self._is_same_page(url)
        else:
            self.finish = True
            self.running = False
            return False

    def _is_same_query(self, page_link):
        parsed_url = parse.urlparse(page_link)
        query = parse.parse_qsl(parsed_url.query)
        query_len = len(query)
        if query_len > 0:
            for index in self.crawled_links:
                for link in self.crawled_links[index]['url'].keys():
                    parsed_link = parse.urlparse(link)
                    link_query = parse.parse_qsl(parsed_link.query)
                    if (parsed_link.path == parsed_url.path) and (len(link_query) == query_len):
                        i = n = 0
                        while i < query_len:
                            if query[i][0] == link_query[i][0]:
                                n += 1
                            i += 1
                        if n == query_len:
                            # result = self._is_same_page(page_link)
                            # return result
                            self._instance.change_state.emit('URL is invalid!')
                            return False
        return True

    # check if given url belongs to website
    # i.e. is in the website's domain
    def _in_domain(self, url):
        if self.base_url in url:  # result = 0 meaning url belongs to website
            return True
        else:
            self._instance.change_state.emit('URL is invalid!')
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            return False

    # check for url protocol
    def _check_protocol(self, url):
        parsed = parse.urlparse(url)  # parse url to get information from it
        protocol = str.lower(str(parsed[0]))  # get url protocol
        if protocol == "http" or protocol == "https":  # is protocol 'http' or 'https'
            return True
        else:
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            self._instance.change_state.emit('URL is invalid!')
            return False

    def _is_robot_allowed(self, path):
        if self._rb_parser:
            return self._rb_parser.is_allowed(self._user_agent, path)
        else:
            return True

    def _url_wise(self, url):
        return self._in_domain(url) and self._check_protocol(url) and self._is_same_query(url)

    def _is_url_good(self, url):
        return self._url_wise(url) and self._page_wise(url)

    def _at_login(self, url):
        if not self.login_url or self.login_url != str(url):
            return False
        elif self.login_url == str(url):
            return True

    def _check_login(self, parsed):
        if self.info['logged_in']:
            self._instance.change_state.emit('Logging into the website...')
            handel = BeyondLogin(self.browser)
            self._logged_in = handel.get_login_info(self.info)
            parent = self._check_parent(handel.login_url)
            if self._logged_in:
                self._instance.change_state.emit('Login Successful!')
                sleep(2)
                if parent:
                    self._add_crawled(handel.login_url, parent, parsed)
                else:
                    self._add_crawled(handel.login_url, self.base_url, parsed)
            else:
                self._instance.change_state.emit('Login Failed!')

            self._links_to_crawl.append([handel.login_url, handel.redirect_url])
        else:
            self._instance.change_state.emit('Login Successful!')
            self._logged_in = True

    def _check_parent(self, url):
        for child in self._links_to_crawl:
            if child[1] == url:
                return child[0]
        return None

    # get all links in a given page
    def _get_page_links(self, url, page):
        self._instance.change_state.emit('Searching for all links in page...')
        # gets a list of all <a> tags in page
        links_tags = page.find_all("a")
        # going through each link
        for link in links_tags:
            self._instance.change_state.emit('Searching for all links in page...')
            link_href = link.get("href")  # get <a> tag link reference. example: <a href="page.html"> ==> page.html
            # check that: link isn't already listed + link isn't blank
            link_listed = self._is_link_listed(link_href)
            if (not link_listed) and ('#' not in str(link_href)):
                # add link to list of links to open
                self._links_to_crawl.append([url, link_href])
                self.total += 1

        forms = page.find_all("form")
        for form in forms:
            action = form.get("action")
            if action:  # link isn't blank
                # check that: link isn't already listed +
                link_listed = self._is_link_listed(action)
                if (not link_listed) and (action != "#"):
                    # add link to list of links to open
                    self._links_to_crawl.append([url, action])
                    self.total += 1
        self._instance.show_total.emit(self.total)

        image_map = page.find_all('area')
        for area in image_map:
            href = area.get('href')  # get 'href' attribute from <area shape="rect" href="#main"> tag
            listed = self._is_link_listed(href)
            if (not listed) and ('#' not in href):
                # add link to list of links to open
                self._links_to_crawl.append([url, href])
                self.total += 1
        self._instance.show_total.emit(self.total)

    # open a page and get its content
    def _open_url(self, url):
        if self.running:
            self._instance.change_state.emit('Pausing between requests...')
            # get page content
            # get page content
            parsed = self.browser.parsed
            if self.info['max_crawl'] != 1:
                self._get_page_links(url, parsed)  # send content to retrieve links from

                sleep(self.delay)
            else:
                self._add_crawled(url, url, parsed)
                self._is_dynamic(url)
                self._instance.show_total.emit(self.total_crawled)
            if self._at_login(url) and not self._logged_in:
                self._check_login(parsed)
            return parsed

    def _add_crawled(self, url, parent, parsed_page):
        self._instance.change_state.emit('Adding new crawled link...')
        found = False
        try:
            title = parsed_page.find('title')
            if not title:
                title = 'NO-TITLE'
            else:
                title = title.text
        except:
            title = 'NO-TITLE'

        for index in self.crawled_links:
            if self.crawled_links[index]['from'] == parent:
                self.crawled_links[index]['url'][url] = title
                found = True
                break
        if not found:
            self.crawled_links[self.total_crawled] = {'from': parent, 'url': {url: title}}
            self.total_crawled += 1
        self.__parsed_crawled[url] = parsed_page
        self._instance.on_info.emit(self.crawled_links)
        sleep(2)

    # main spider function; creates our spider's web
    def run(self):
        self.start = datetime.now().time()
        self._opener(self.base_url)
        self._open_url(self.base_url)  # send main url to be opened and checked
        self._elapsed = self.browser.state.response.elapsed.total_seconds()
        self._compute_crawl_delay()
        # while there are still links to open
        self.i = len(self._links_to_crawl) - 1
        while (len(self._links_to_crawl)) > 0 and (self._crawled_max()) and not self.finish:
            self._instance.change_state.emit('Crawling...')
            # start from the last link in the list
            parent = self._links_to_crawl[self.i][0]
            link = self._links_to_crawl[self.i][1]
            url = parse.urljoin(self.base_url, link)  # join main url with page link
            if self._is_url_good(url) and self._is_robot_allowed(link):  # is url valid and working
                self._instance.change_state.emit('URL is good!')
                parsed_page = self._open_url(url)  # open page
                self._add_crawled(url, parent, parsed_page)
                self._compute_crawl_delay()
                # add link to list of opened links
                self._is_dynamic(url)
            else:
                self._instance.change_state.emit('URL is not good!')
            # delete opened link from list of links to open
            self._links_to_crawl.pop(self.i)
            if self.i > 0:
                self.i = self.i - 1
            elif self.i == 0:
                self.i = len(self._links_to_crawl) - 1
            if len(self._links_to_crawl) == 0 or self.i < 0:
                self._instance.change_state.emit('Finished.')
                self.finish = True
                break
        self.finish = True
        self._instance.crawl_finished.emit(self._wrap_up())

    def _calc_time(self):
        finish = datetime.now().time()
        delta1 = timedelta(seconds=self.start.second, microseconds=self.start.microsecond,
                           minutes=self.start.minute, hours=self.start.hour)
        delta2 = timedelta(seconds=finish.second, microseconds=finish.microsecond,
                           minutes=finish.minute, hours=finish.hour)
        taken = delta2 - delta1
        seconds = round(taken.total_seconds())
        if seconds >= 3600:
            hours = round(seconds / 3600)
            minutes = (round((seconds / 3600) / 60))
            elapsed = str(hours) + ':' + str(minutes) + ' hrs'
        elif seconds >= 60:
            minutes = round(seconds / 60)
            seconds = round(seconds % 60)
            elapsed = str(str(minutes) + '.' + str(seconds) + ' mins')
        else:
            elapsed = str(seconds) + ' secs'
        return elapsed

    def _wrap_up(self):
        wrap = {
            'links': self.crawled_links,
            'dynamic': self.dynamic,
            'total_crawled': self.total_links(),
            'total': self.total,
            'invalid': self.invalid_links_count,
            'running': self.running,
            'time': self._calc_time()
        }
        return wrap
