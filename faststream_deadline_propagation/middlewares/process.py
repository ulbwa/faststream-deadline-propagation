import asyncio
from datetime import datetime
from functools import partial
from typing import Any, Callable

from faststream import BaseMiddleware, context
from faststream.broker.message import StreamMessage
from faststream.types import AsyncFuncAny

from faststream_deadline_propagation.countdown import _DeadlineCountdown
from faststream_deadline_propagation.defaults import _COUNTDOWN_CONTEXT, DEFAULT_HEADER
from faststream_deadline_propagation.exceptions import DeadlineOccurred


class DeadlineProcessMiddleware(BaseMiddleware):
    def __init__(self, msg: Any, *, header: str):
        self.header = header

        super().__init__(msg)

    @classmethod
    def make_middleware(
        cls, header: str = DEFAULT_HEADER
    ) -> Callable[[Any], "DeadlineProcessMiddleware"]:
        return partial(cls, header=header)

    async def consume_scope(
        self, call_next: "AsyncFuncAny", msg: "StreamMessage[Any]"
    ) -> Any:
        if not (deadline_value := msg.headers.get(DEFAULT_HEADER)):
            return await call_next(msg)

        deadline = datetime.fromisoformat(deadline_value)
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
