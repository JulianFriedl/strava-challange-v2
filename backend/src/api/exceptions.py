class AuthorizationError(Exception):
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.status_code = status_code


class ScopeError(Exception):
    def __init__(self, message, status_code=403):
        super().__init__(message)
        self.status_code = status_code

class ParamError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code
