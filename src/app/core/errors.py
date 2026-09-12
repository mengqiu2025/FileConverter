class ConverterError(Exception):
    """Base class for converter errors."""


class SameFormatError(ConverterError):
    """Raised when the source and target formats are identical."""


class UnsupportedFormatError(ConverterError):
    """Raised when a file extension is not supported."""


class EngineNotFoundError(ConverterError):
    """Raised when a required external engine cannot be located."""
