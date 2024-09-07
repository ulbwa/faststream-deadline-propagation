import asyncio
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Callable

from faststream import BaseMiddleware, context
from faststream.broker.message import StreamMessage
from faststream.types import AsyncFuncAny

from faststream_deadline_propagation.countdown import _DeadlineCountdown
from faststream_deadline_propagation.defaults import _COUNTDOWN_CONTEXT, DEFAULT_HEADER
from faststream_deadline_propagation.exceptions import DeadlineOccurred


class DeadlineProcessMiddleware(BaseMiddleware):
    def __init__(self, msg: Any, *, header: str, default_timeout: float | None = None):
        self.header = header
        self.default_timeout = default_timeout

        super().__init__(msg)

    @classmethod
    def make_middleware(
        cls, header: str = DEFAULT_HEADER, default_timeout: float | None = None
    ) -> Callable[[Any], "DeadlineProcessMiddleware"]:
        return partial(cls, header=header, default_timeout=default_timeout)

    async def consume_scope(
        self, call_next: "AsyncFuncAny", msg: "StreamMessage[Any]"
    ) -> Any:
        if deadline_value := msg.headers.get(DEFAULT_HEADER):
            deadline = datetime.fromisoformat(deadline_value)
        elif self.default_timeout is not None:
            deadline = datetime.now() + timedelta(seconds=self.default_timeout)
        else:
            return await call_next(msg)

        countdown = _DeadlineCountdown(deadline=deadline)
        context.set_local(_COUNTDOWN_CONTEXT, countdown)

        if countdown() <= 0:
            raise DeadlineOccurred()

        try:
            async with asyncio.timeout(countdown()):
                return await call_next(msg)
        except TimeoutError as exc:
            raise DeadlineOccurred() from exc


__all__ = ("DeadlineProcessMiddleware",)
