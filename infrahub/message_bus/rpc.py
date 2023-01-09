from __future__ import annotations

import asyncio
import uuid
from typing import MutableMapping, Any

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustConnection,
)

import infrahub.config as config

from . import get_broker
from .events import InfrahubRPC, InfrahubMessage


class InfrahubRpcClient:
    connection: AbstractRobustConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self) -> InfrahubRpcClient:
        self.connection = await get_broker()

        if not self.connection:
            return self

        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: AbstractIncomingMessage) -> None:
        if message.correlation_id is None:
            print(f"Bad message {message!r}")
            return

        future: asyncio.Future = self.futures.pop(message.correlation_id)

        if future:
            future.set_result(InfrahubMessage.convert(message))

    async def call(self, message: InfrahubRPC, wait_for_response: bool = True) -> Any:
        correlation_id = str(uuid.uuid4())

        if wait_for_response:
            future = self.loop.create_future()
            self.futures[correlation_id] = future
        else:
            self.futures[correlation_id] = None

        await message.send(channel=self.channel, correlation_id=correlation_id, reply_to=self.callback_queue.name)

        if wait_for_response:
            return await future
        else:
            return
