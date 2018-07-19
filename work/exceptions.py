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


class LoginError(Exception):
    def __init__(self, message="Credentials are Possibly Wrong!", errors=None, *args):
        self.message = message
        super().__init__(self.message)
        self.errors = errors


class FieldsError(Exception):
    def __init__(self, message="Couldn't Find Appropriate Fields!", errors=None, *args):
        self.message = message
        super().__init__(self.message)
        self.errors = errors


class InvalidFormError(Exception):
    def __init__(self, message="Form isn't Suitable For Attack!", errors=None, *args):
        self.message = message
        super().__init__(self.message)
        self.errors = errors


class FilledFieldError(Exception):
    def __init__(self, message="Some form fields are already filled!", errors=None, *args):
        self.message = message
        super().__init__(self.message)
        self.errors = errors
