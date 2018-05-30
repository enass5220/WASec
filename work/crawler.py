'''
  created: 16-Jan-2018
  updated: 18-Jan-2018 [ added login ]
  updated: 22-Jan-2018 [ upgraded to Python3 ]
  updated: 25-Jan-2018 [ working with Python3 ]
  ####
  this is a poorly written crawler
  that gets a list of all links in a website.
  However, I'm a proud mommy of it <<<333 (three in-boxed hearts)
  -the end
'''

# TODO: request timeout
# TODO: try and follow buttons, see new links they take you to
# TODO: pop-window to enter credentials in case it reaches login page
# NOTE: lags when tested on actual sites + login conformation is not yet well implemented

from urllib import parse
from bs4 import BeautifulSoup  # Helps parsing HTML webpages
from beyondlogin import BeyondLogin
from time import sleep
from robobrowser import browser  # Helps generating requests for webpages
from robotexclusionrulesparser import RobotExclusionRulesParser
from logindialog_work import Work_LoginDialog
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal


class CrawlerWorker(QThread):  # spider that will get links of website # called to create instance of the class
    on_info = pyqtSignal(dict)

    def __init__(self, info, instance, parent=None):
        QThread.__init__(self, parent)
        self.instance = instance
        self.pause = False
        self.on_info.connect(self.populate_tree)
        self.running = True
        self.base_url = info['base_url']  # main url of website
        self._links_to_crawl = []  # list of links yet to open
        self.crawled_links = {}  # dictionary of links opened/all links
        self.total = 0  # total number of links in website
        self.max_pages = info['max_crawl']  # max pages to crawl
        self.invalid_links_count = 0  # number of broken links found
        self.invalid_links_list = []  # list of broken links found
        self.dynamic = []
        self.login_info = {}
        self.login_url = info['login_url']  # login page url if available
        if info['robo_url']:
            self._rb_parser = RobotExclusionRulesParser()
            self._rb_parser.fetch(info['robo_url'])
            self._user_agent = 'WASec'
        else:
            self._rb_parser = None
        self.browser = browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
        self._logged_in = False

    # get total number of links opened so far
    def total_links(self):
        self.total = len(self.crawled_links)
        return self.total

    # check if max pages reached
    def __crawled_max(self):
        result = (self.max_pages == 0) or (self.max_pages < self.total_links())
        return result

    # is link already listed
    def __is_link_listed(self, link):
        url = parse.urljoin(self.base_url, link)
        result = False
        for index in self.crawled_links:
            for opened in self.crawled_links[index]['url']:
                if url == opened or link == opened:
                    result = True
        for to_open in self._links_to_crawl:
            if link == to_open or url == to_open:
                result = True
        return result

    # retrieve invalid links
    def invalid_links(self):
        if self.invalid_links_count > 0:
            print("Found %s broken links:" % self.invalid_links_count)
            for link in self.invalid_links_list:
                print(link)
        else:
            print("No invalid links found.")

    # gets dynamic urls
    def __is_dynamic(self, url):
        if '?' in str(url) or '=' in str(url):
            self.dynamic.append(url)

    # check if page opened and exists
    def __is_response_ok(self, url):
        self.browser.open(url)  # open given url of page
        # status_code 200 means OK; no problems with page
        if '200' in str(self.browser.response):
            return True
        else:
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            return False

    def __is_html_page(self, url):
        request = self.browser.session.head(url)
        if "text/html" in str.lower(request.headers["content-type"]):
            return True
        else:
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            return False

    def __is_same_page(self, page_link):
        self.browser.open(page_link)
        page = self.browser.parsed
        for index in self.crawled_links:
            for link in self.crawled_links[index]['url']:
                self.browser.open(link)
                check = self.browser.parsed
                if check == page:
                    return False
        return True

    def __page_wise(self, url):
        return self.__is_response_ok(url) and self.__is_html_page(url) and self.__is_same_page(url)

    def __is_same_query(self, page_link):
        parsed_url = parse.urlparse(page_link)
        query = parse.parse_qsl(parsed_url.query)
        query_len = len(query)
        if query_len > 0:
            for index in self.crawled_links:
                for link in self.crawled_links[index]['url']:
                    parsed_link = parse.urlparse(link)
                    link_query = parse.parse_qsl(parsed_link.query)
                    if (parsed_link.path == parsed_url.path) and (len(link_query) == query_len):
                        i = n = 0
                        while i < query_len:
                            if query[i][0] == link_query[i][0]:
                                n += 1
                            i += 1
                        if n == query_len:
                            return False
        return True

    # check if given url belongs to website
    # i.e. is in the website's domain
    def __in_domain(self, url):
        url = str(url)
        base = str(self.base_url)
        end = len(base)  # get last position in base url
        if base.rfind('/') != end - 1:
            path = base.rfind('/') + 1  # get position of last slash
            base = base.rstrip(base[path:end])
        result = str.find(url, base, 0, end)  # find if website url exists in given url
        if result == 0:  # result = 0 meaning url belongs to website
            return True
        else:
            return False

    # check for url protocol
    def __check_protocol(self, url):
        parsed = parse.urlparse(url)  # parse url to get information from it
        protocol = str.lower(str(parsed[0]))  # get url protocol
        if protocol == "http" or protocol == "https":  # is protocol 'http' or 'https'
            return True
        else:
            self.invalid_links_count += 1
            self.invalid_links_list.append(url)
            return False

    def __is_robot_allowed(self, url):
        if self._rb_parser:
            return self._rb_parser.is_allowed(self._user_agent, url)
        else:
            return True

    def __url_wise(self, url):
        return self.__is_robot_allowed(url) and self.__in_domain(url) and self.__check_protocol(
            url) and self.__is_same_query(url)

    def __is__url_good(self, url):
        return self.__url_wise(url) and self.__page_wise(url)

    def __at_login(self, url):
        if not self.login_url or self.login_url != str(url):
            return False
        elif self.login_url == str(url):
            return True  # TODO: add alert to screen to enter credentials

    def __beyond_login(self, url):
        try:
            self.window = QtWidgets.QDialog()
            browser.RoboBrowser(parser="html.parser", user_agent="WASecBot")
            self.handel = BeyondLogin(browser, self.info['login_url'])
            self.ui = Work_LoginDialog(self, parent=self)
            self.ui.go()
            self.check_login()
        except Exception as e:
            print(str(e))

    def check_login(self):
        if self.handel.logged_in:
            if not self.window.isHidden(): self.window.hide()
            self._logged_in = self.handel.logged_in
            self.running = True
        else:
            self.running = False

    # get all links in a given page
    def __get_page_links(self, url, page):
        # gets a list of all <a> tags in page
        links_tags = page.find_all("a")
        # going through each link
        for link in links_tags:
            link_href = link.get("href")  # get <a> tag link reference. example: <a href="page.html"> ==> page.html
            # check that: link isn't already listed + link isn't blank
            link_listed = self.__is_link_listed(link_href)
            if (not link_listed) and (link_href != "#"):
                # add link to list of links to open
                self._links_to_crawl.append([url, link_href])
        forms = page.find_all("form")
        for form in forms:
            action = form.get("action")
            if action:  # link isn't blank
                # check that: link isn't already listed +
                link_listed = self.__is_link_listed(action)
                if (not link_listed) and (action != "#"):
                    # add link to list of links to open
                    self._links_to_crawl.append([url, action])

    # open a page and get its content
    def __open__url(self, url):
        # get page content
        self.browser.open(url=url)
        parsed = str(self.browser.parsed)
        content = BeautifulSoup(parsed, 'html.parser')
        self.__get_page_links(url, content)  # send content to retrieve links from
        if self.__at_login(url) and not self._logged_in:
            self.running = False
            self.__beyond_login(url)

    def __add_crawled(self, url, parent):
        pos = -1
        for index in self.crawled_links:
            if self.crawled_links[index]['from'] == parent:
                self.crawled_links[index]['url'].add(url)
                pos = index
                break
        if pos == -1:
            self.crawled_links[self.total] = {'from': parent, 'url': {url}}
            self.total += 1

    # main spider function; creates our spider's web
    def run(self):
        self.__open__url(self.base_url)  # send main url to be opened and checked
        self._links_to_crawl.append([self.base_url, self.base_url])
        # while there are still links to open
        i = len(self._links_to_crawl) - 1
        while len(self._links_to_crawl) != 0 and self.__crawled_max():
            if self.running:
                # start from the last link in the list
                if i != 0:
                    i = i - 1
                else:
                    i = len(self._links_to_crawl) - 1
                parent = self._links_to_crawl[i][0]
                link = self._links_to_crawl[i][1]
                url = parse.urljoin(self.base_url, link)  # join main url with page link
                if self.__is__url_good(url):  # is url valid and working
                    self.__open__url(url)  # open page
                    # add link to list of opened links
                    if self.running:
                        self.on_info.emit(self.crawled_links)
                        self.__add_crawled(url, parent)
                        self.__is_dynamic(url)
                    self.sleep(5)
                # delete opened link from list of links to open
                if self.running: self._links_to_crawl.pop(i)
            else:
                break
                #self.check_login()
                #self.wait(2)

    # prints all links of website
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
