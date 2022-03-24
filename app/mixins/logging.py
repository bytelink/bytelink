from ..utils import Logger


class LoggingMixin:
    @property
    def logger(self) -> Logger:
        try:
            return self._log
        except AttributeError:
            self._log = Logger()
            return self._log
