"""
Module containing all custom exceptions used by TarjanPlanner
"""

# base exception


class BaseTarjanException(Exception):
    """
    Base exception for TarjanPlanner. Only used for deriving new exceptions containing additional
    relevant information for debugging
    """

    def __init__(self, msg, *, additional_info=None):
        super().__init__(msg)
        self.additional_info = additional_info


# logger exceptions


class LoggingSetupFailed(BaseTarjanException):
    """
    Used when setting up the logger. Will be thrown if anything fails at that step
    """


# relatives manager exceptions


class RMSetupFailed(BaseTarjanException):
    """
    Used exclusively if setting up the relatives manager fails
    """


class RMAddRelativeFailed(BaseTarjanException):
    """
    Used when adding a new contact, and passing invalid parameters
    """


# route computing exceptions


class ModesImportFailed(BaseTarjanException):
    """
    Used exclusively when importing modes of transport
    """


class RouteCalculationError(BaseTarjanException):
    """
    Used if calculating an optimal route fails
    """


class RouteDisplayingError(BaseTarjanException):
    """
    Used if displaying an optimal route fails
    """
