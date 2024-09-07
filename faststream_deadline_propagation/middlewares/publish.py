from datetime import datetime
from functools import partial
from time import time
from typing import Any, Callable

from faststream import BaseMiddleware
from faststream.types import AsyncFunc

from faststream_deadline_propagation.defaults import DEFAULT_HEADER, DEFAULT_TIMEOUT


class DeadlinePublishMiddleware(BaseMiddleware):
    def __init__(self, msg: Any, *, header: str):
        self.header = header

        super().__init__(msg)

    @classmethod
    def make_middleware(
        cls, header: str = DEFAULT_HEADER
    ) -> Callable[[Any], "DeadlinePublishMiddleware"]:
        return partial(cls, header=header)

    async def publish_scope(
        self,
        call_next: "AsyncFunc",
        msg: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not kwargs["headers"]:
            kwargs["headers"] = dict()

        if self.header in kwargs["headers"]:
            return await call_next(msg, *args, **kwargs)

        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        elif "rpc_timeout" in kwargs:
            timeout = kwargs["rpc_timeout"]
        else:
            timeout = DEFAULT_TIMEOUT

        deadline = datetime.fromtimestamp(time() + timeout)
        kwargs["headers"][self.header] = deadline.isoformat()

        return await call_next(msg, *args, **kwargs)


__all__ = ("DeadlinePublishMiddleware",)
