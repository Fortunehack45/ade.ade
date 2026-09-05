"""Control flow signals for loops and function returns."""

from ade.runtime.value import AdeValue, AdeNull


class ReturnSignal(Exception):
    """Signal raised to unwind execution upon encountering a return statement."""

    def __init__(self, value: AdeValue = AdeNull.INSTANCE):
        self.value = value


class BreakSignal(Exception):
    """Signal raised to exit the current loop."""
    pass


class ContinueSignal(Exception):
    """Signal raised to jump to the next iteration of the current loop."""
    pass
