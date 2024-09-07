from datetime import datetime
from time import time
from typing import Annotated

from faststream import Context

from faststream_deadline_propagation.defaults import _COUNTDOWN_CONTEXT
from faststream_deadline_propagation.exceptions import DeadlineOccurred


class _DeadlineCountdown:
    def __init__(self, deadline: datetime):
        self.deadline = deadline.timestamp()

    def __call__(self) -> float:
        timeout = self.deadline - time()
        if timeout <= 0:
            raise DeadlineOccurred()
        return timeout


DeadlineCountdown = Annotated[_DeadlineCountdown, Context(_COUNTDOWN_CONTEXT)]


__all__ = "_DeadlineCountdown", "DeadlineCountdown"
