"""Serialised, rate-limited gateway for outgoing Open3e commands.

Every command the integration sends to the Open3e server (reads and writes
alike) travels over a single MQTT command topic and is translated by the server
into UDS requests on the heat-pump CAN bus. That bus - and the ``udsoncan``
stack on the server - only tolerates one in-flight request at a time.

Bursts of commands therefore risk wedging the server: it starts answering every
request with ``Did not receive response in time. Global request timeout time
has expired (timeout=3.000 sec)`` and only a restart of the Open3e container
clears it. The most reliable way to trigger this is the flood of read requests
the integration issues while Home Assistant is (re)starting, or a request that
is still being sent while Home Assistant is shutting down.

``Open3eCommandGate`` funnels every such publish through one lock, enforces a
minimum spacing between consecutive commands, and can be paused so that no
further commands leave the integration once Home Assistant begins shutting down
or the config entry is unloaded.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

_LOGGER = logging.getLogger(__name__)

DEFAULT_MIN_INTERVAL = 0.25
"""Minimum number of seconds between two consecutive commands to the server."""


class Open3eCommandGate:
    """Serialise and pace outgoing Open3e commands."""

    __min_interval: float
    __lock: asyncio.Lock
    __last_send: float
    __paused: bool

    def __init__(self, min_interval: float = DEFAULT_MIN_INTERVAL) -> None:
        self.__min_interval = min_interval
        self.__lock = asyncio.Lock()
        self.__last_send = 0.0
        self.__paused = False

    @property
    def paused(self) -> bool:
        """Return whether the gate currently rejects new commands."""
        return self.__paused

    def pause(self) -> None:
        """Stop letting commands through (e.g. on shutdown / unload).

        A command still waiting its turn inside :meth:`async_send` is dropped
        rather than sent; one already handed to the transport runs to
        completion.
        """
        self.__paused = True

    def resume(self) -> None:
        """Allow commands through again and reset the pacing window."""
        self.__paused = False
        self.__last_send = 0.0

    async def async_send(self, send: Callable[[], Awaitable[None]]) -> bool:
        """Run ``send`` once it is this command's turn.

        Commands run one at a time and never closer together than
        ``min_interval`` seconds. If the gate is paused the command is dropped
        and ``False`` is returned so the caller can treat it as "not sent".
        """
        if self.__paused:
            _LOGGER.debug("Command gate paused; dropping outgoing Open3e command")
            return False

        async with self.__lock:
            # The gate may have been paused while we waited for the lock.
            if self.__paused:
                _LOGGER.debug("Command gate paused; dropping outgoing Open3e command")
                return False

            wait = self.__min_interval - (time.monotonic() - self.__last_send)
            if wait > 0:
                await asyncio.sleep(wait)

            # The gate may have been paused during the pacing sleep.
            if self.__paused:
                _LOGGER.debug("Command gate paused; dropping outgoing Open3e command")
                return False

            try:
                await send()
            finally:
                self.__last_send = time.monotonic()

            return True
