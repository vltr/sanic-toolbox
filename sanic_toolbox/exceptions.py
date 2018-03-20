class SanicToolboxException(Exception):
    pass


class BeforeAndAfterNotSupported(SanicToolboxException):
    pass


class ListenerNotFound(SanicToolboxException):
    pass


class TaskNotFound(SanicToolboxException):
    pass


class MiddlewareNotFound(SanicToolboxException):
    pass
