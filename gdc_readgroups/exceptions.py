"""
Exceptions for Read Group headers
"""

class NoReadGroupError(Exception):
    """NoReadGroupError"""

class SamtoolsViewError(Exception):
    """SamtoolsViewError"""

class InvalidPlatformError(Exception):
    """InvalidPlatformError"""

class InvalidPlatformModelError(Exception):
    """InvalidPlatformError"""

class MissingReadgroupIdError(Exception):
    """MissingReadgroupIdError"""

class InvalidDatetimeError(Exception):
    """InvalidDatetimeError"""

class NotABamError(Exception):
    """NotABamError"""
