# faststream-deadline-propagation

A middleware for the FastStream framework that provides deadline-propagation in Remote Procedure
Call requests. It ensures that messages are processed within a specified timeout period, raising
an exception if the deadline is exceeded.

## Features

- **Deadline Processing Middleware**: Ensures that message processing is completed within a 
specified deadline.
- **Deadline Publishing Middleware**: Adds a deadline header to messages being published, 
ensuring they are processed within the specified timeout.
- **Customizable Header**: Allows customization of the header used for deadlines.
- **Exception Handling**: Raises a `DeadlineOccurred` exception if the deadline is exceeded.

## Example

```python
import asyncio
from datetime import datetime, timedelta
from typing import Any

from faststream import FastStream
from faststream.nats import NatsBroker, NatsRouter

from faststream_deadline_propagation import (
    DeadlineCountdown,
    DeadlineProcessMiddleware,
    DeadlinePublishMiddleware,
)

rpc_router = NatsRouter(
    middlewares=(
        DeadlineProcessMiddleware.make_middleware(),
        # Your other middlewares here
    )
)
broker = NatsBroker(
    middlewares=(
        # Your other middlewares here
        DeadlinePublishMiddleware.make_middleware(),
    )
)


@rpc_router.subscriber("something")
async def do_nothing(message: Any, countdown: DeadlineCountdown):
    await asyncio.sleep(1)

    # current timeout in seconds
    current_timeout: float = countdown()
    print(current_timeout)


broker.include_routers(rpc_router)
app = FastStream(broker)


@app.after_startup
async def publisher():
    # You can specify a timeout and the DeadlinePublishMiddleware will automatically
    # add the header
    await broker.request(123, "something", timeout=3)

    # Or explicitly specify the header with your deadline, in this case, the header value
    # will not be overridden
    await broker.request(
        123,
        "something",
        timeout=3,
        headers={"x-deadline": (datetime.now() + timedelta(seconds=1)).isoformat()},
    )
```

To handle the `DeadlineOccurred` error and serialize the response, you should use the 
[`ExceptionMiddleware`](https://faststream.airt.ai/latest/getting-started/middlewares/exception/) 
built into FastStream.
