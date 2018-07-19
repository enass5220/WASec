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

from exceptions import FieldsError, InvalidFormError, FilledFieldError
from robobrowser.forms.fields import Submit
from  robobrowser.exceptions import InvalidNameError

class FormHandler:
    def __init__(self, browser):
        self.attack_fields = []
        self.checkboxes = {}
        self.radios = {}
        self.selects = {}
        self.submit_buttons = []
        self.other_fields = {}
        self.fault_type = None
        self.browser = browser

    def parser(self, form):
        try:
            parsed_form = form.parsed
            if parsed_form.get('enctype') == 'multipart/form-data':
                raise InvalidFormError(errors="Form 'Enctype' is 'multipart/form-data'")
            fields = parsed_form.find_all('input')
            filled = 0
            text = 0
            for field in fields:
                if field['type'] == 'submit':
                    if field.has_attr('name'):
                        name = field['name']
                        self.submit_buttons.append(form[name])
                    else:
                        self.submit_buttons.append('NA')

                elif field['type'] == 'text':
                    text += 1
                    if field.has_attr('value'):
                       filled += 1
                    else:
                        self.attack_fields.append(field['name'])
                elif field['type'] == 'hidden':
                    if 'token' in field['name']:
                        self.other_fields['csrf-token'] = {'name': field['name'], 'value': field['value']}
                    else:
                        text += 1
                        if field.has_attr('value'):
                            filled += 1
                        else:
                            self.attack_fields.append(field['name'])
                elif field['type'] == 'checkbox':
                    tick = form[field['name']].options
                    self.checkboxes[field['name']] = tick

                elif field['type'] == 'radio':
                    # check if radio is ticked if it exists in radios dict
                    ticked = self.radios.get(field['name'])
                    if not ticked:
                        # pick the first option
                        tick = form[field['name']].options[0]
                        # add radio name and desired value to radios dict
                        self.radios[field['name']] = tick
            if not self.submit_buttons:
                buttons = parsed_form.find_all('button')
                for button in buttons:
                    if button.has_attr('type') and button.has_attr('name') and button['type'] == 'submit':
                        submit = Submit(button)
                        self.submit_buttons.append(submit)
            if not self.submit_buttons:
                self.submit_buttons.append('NA')
            if not self.attack_fields:
                raise FieldsError(
                    "Can't Find Fields Suitable for Attack i.e. not of type 'Text' or 'Hidden'")
            if not self.submit_buttons:
                raise FieldsError("Can't Find Submit Button!")

            #if filled == text:
                #raise FilledFieldError
            select_fields = parsed_form.find_all('select')
            for select in select_fields:
                # select first value
                option = form[select['name']].options[0]
                self.selects[select['name']] = option

            textbox = parsed_form.find_all('textarea')
            i = 0
            for box in textbox:
                self.other_fields['textarea-' + str(i)] = {'name': box['name']}
                i += 1

            i = 0
            emails = parsed_form.find_all('email')
            for email in emails:
                self.other_fields['email-' + str(i)] = {'name': email['name']}
                i += 1

            return True

        except TypeError as Terror:  # When you don't pass correct type of variable
            self.fault_type = {'fault': "TypeError - Invalid type of variable!" + str(Terror)}
            return False
        except AttributeError as Aerror:  # variable doesn't have desired attribute
            self.fault_type = {'fault': "AttributeError - Invalid attribute" + str(Aerror)}
            return False
        except NameError as Nerror:
            self.fault_type = {'fault': "NameError - Variable not found" + str(Nerror)}
            return False
        except FieldsError as Ferror:
            self.fault_type = {'fault': "FieldsError - " + str(Ferror)}
            return False
        except InvalidFormError as Ierror:
            self.fault_type = {'fault': "InvalidFormError - " + str(Ierror)}
            return False
        except FilledFieldError as FFerror:
            self.fault_type = {'fault': "FilledFieldError - " + str(FFerror)}
            return False
        except InvalidNameError as INError:
            self.fault_type = {'fault': "InvalidNameError - " + str(INError)}
            return False
            #   throw
            #   finally: #  finish
                # check if there are any list boxes

