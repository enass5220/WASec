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
