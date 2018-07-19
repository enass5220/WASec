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

from robobrowser.forms.fields import Submit
from exceptions import LoginError, FieldsError


class BeyondLogin:
    def __init__(self, browser):
        self.logged_in = False
        self.fields_not_found = False
        self._browser = browser
        self.login_url = self.__user = self.__password = self.redirect_url = None

    def get_login_info(self, info):
        self.login_url = info['login_url']
        self.__user = info['user']
        self.__password = info['pass']
        self.redirect_url = info['redirect_url']
        self.logged_in = self.login()
        return self.logged_in

    def __fetch_form(self):
        self._browser.open(url=self.login_url)
        forms = self._browser.get_forms()
        for form in forms:
            html_form = form.parsed
            user_field = None
            password_field = None
            submit_button = None
            token = None
            inputs = html_form.find_all('input')
            for item in inputs:
                if item['type'] == 'password':
                    password_field = item['name']
                elif (item['type'] == 'email') or (item['type'] == 'text'):
                    user_field = item['name']
                elif item['type'] == 'submit':
                    if item.has_attr('name'):
                        submit_button = form[item['name']]
                    else:
                        submit_button = 'NA'

                elif item['type'] == 'hidden' and 'token' in item['name']:
                    token = {
                        'name': item['name'],
                        'value': item['value']
                    }

            if not submit_button:
                buttons = html_form.find_all('button')
                for button in buttons:
                    if button['type'] == 'submit':
                        #button['name'] = None
                        submit = Submit(button)
                        submit_button = submit
            if not password_field:
                self.fields_not_found = True
            else:
                self.fields_not_found = False
            if (user_field is not None) and (password_field is not None) and (submit_button is not None):
                self.__submit_form(form, user_field, password_field, submit_button, token)
                break
        if self.fields_not_found:
            raise FieldsError
        elif not self.logged_in:
            raise LoginError

    def __submit_form(self, form, user_field, password_field, submit_button, token):
        login_page = self._browser.parsed
        form[user_field].value = self.__user
        form[password_field].value = self.__password
        if submit_button != 'NA' and submit_button.name not in form.submit_fields.keys():
            form.add_field(submit_button)
        if token:
            form[token['name']].value = token['value']
        if submit_button != 'NA':
            self._browser.submit_form(form, submit=submit_button)
        elif submit_button == 'NA':
            self._browser.submit_form(form)
        else:
            raise FieldsError
        # check if login was successful
        response_url = str(self._browser.url)
        response_page = self._browser.parsed
        if (response_url == self.redirect_url) and (response_page != login_page):
            self.logged_in = True
        else:
            self.logged_in = False

    def login(self):
        self.__fetch_form()
        if self.logged_in:
            return self.logged_in
        else:
            return False
