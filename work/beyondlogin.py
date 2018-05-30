'''
    updated: 22-Jan-2018 [ upgraded to Python3]
    updated: 26-Jan-2018 [ added Robobrowser implementation ]
'''

from bs4 import BeautifulSoup  # Helps parsing HTML webpages
from exceptions import LoginError, FieldsError

class BeyondLogin:
    def __init__(self, browser, login_url):
        self.logged_in = False
        self.__browser = browser
        self.__login_url = login_url
        self.__user = self.__password = self.redirect_url = None

    def get_login_info(self, info):
        self.__login_url = info['login_url']
        self.__user = info['user']
        self.__password = info['pass']
        self.redirect_url = info['redirect_url']
        self.logged_in = self.login()

    def __fetch_form(self):
        self.__browser.open(url=self.__login_url)
        parsed = str(self.__browser.parsed)
        parse_html = BeautifulSoup(parsed, 'html.parser')
        html_form = parse_html.form
        user_field = None
        password_field = None
        submit_button = None
        inputs = html_form.find_all('input')
        for item in inputs:
            if item['type'] == 'password':
                password_field = item['name']
            elif (item['type'] == 'email') or (item['type'] == 'text'):
                user_field = item['name']
        if (user_field is not None) and (password_field is not None):
            self.__submit_form(user_field, password_field)
        else:
            self.logged_in = False
            raise FieldsError

    def __submit_form(self, user_field, password_field):
        self.__browser.open(self.__login_url, "post")
        login_page = self.__browser.parsed
        form = self.__browser.get_forms()[0]
        form[user_field].value = self.__user
        form[password_field].value = self.__password
        self.__browser.submit_form(form)
        # check if login was successful
        response_url = str(self.__browser.url)
        response_page = self.__browser.parsed
        if (response_url == self.redirect_url) and (response_page != login_page):
            self.logged_in = True
        else:
            self.logged_in = False
            raise LoginError

    def login(self):
        self.__fetch_form()
        if self.logged_in:
            return self.logged_in
        else:
            return False
