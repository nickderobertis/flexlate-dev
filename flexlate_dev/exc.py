class FlexlateDevException(Exception):
    pass


class UserInputException(FlexlateDevException):
    pass


class NoSuchRunConfigurationException(UserInputException):
    pass


class NoSuchDataException(UserInputException):
    pass
