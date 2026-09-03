"""Tests for :mod:`custom_components.open3e.command_gate`.

Run with the standard-library test runner (``scripts/test`` /
``python -m unittest``); a Home Assistant install must be importable because the
package ``__init__`` pulls in ``homeassistant.components.mqtt``.
"""

from __future__ import annotations

import asyncio
import time
import unittest

from custom_components.open3e.command_gate import Open3eCommandGate


class CommandGateTest(unittest.IsolatedAsyncioTestCase):
    async def test_sends_in_order_and_reports_success(self) -> None:
        gate = Open3eCommandGate(min_interval=0)
        seen: list[int] = []

        async def send(tag: int) -> None:
            seen.append(tag)

        results = [await gate.async_send(lambda t=t: send(t)) for t in range(5)]

        self.assertEqual(seen, [0, 1, 2, 3, 4])
        self.assertTrue(all(results))

    async def test_commands_never_overlap(self) -> None:
        gate = Open3eCommandGate(min_interval=0)
        events: list[tuple[str, int]] = []

        async def send(tag: int) -> None:
            events.append(("start", tag))
            await asyncio.sleep(0.02)
            events.append(("end", tag))

        await asyncio.gather(*(gate.async_send(lambda t=t: send(t)) for t in range(4)))

        # Every "start" is immediately followed by its own "end".
        for i in range(0, len(events), 2):
            self.assertEqual(events[i][0], "start")
            self.assertEqual(events[i + 1], ("end", events[i][1]))

    async def test_min_interval_is_enforced(self) -> None:
        gate = Open3eCommandGate(min_interval=0.1)
        stamps: list[float] = []

        async def send() -> None:
            stamps.append(time.monotonic())

        for _ in range(3):
            await gate.async_send(send)

        self.assertGreaterEqual(stamps[1] - stamps[0], 0.09)
        self.assertGreaterEqual(stamps[2] - stamps[1], 0.09)

    async def test_pause_drops_commands(self) -> None:
        gate = Open3eCommandGate(min_interval=0)
        calls = 0

        async def send() -> None:
            nonlocal calls
            calls += 1

        gate.pause()
        self.assertTrue(gate.paused)
        self.assertFalse(await gate.async_send(send))
        self.assertEqual(calls, 0)

        gate.resume()
        self.assertFalse(gate.paused)
        self.assertTrue(await gate.async_send(send))
        self.assertEqual(calls, 1)

    async def test_pause_while_waiting_for_turn_drops_queued_command(self) -> None:
        gate = Open3eCommandGate(min_interval=0)
        started = asyncio.Event()
        release = asyncio.Event()
        second_ran = False

        async def blocker() -> None:
            started.set()
            await release.wait()

        async def second() -> None:
            nonlocal second_ran
            second_ran = True

        first = asyncio.create_task(gate.async_send(blocker))
        await started.wait()

        queued = asyncio.create_task(gate.async_send(second))
        await asyncio.sleep(0)  # let the second call block on the lock

        gate.pause()
        release.set()

        self.assertTrue(await first)
        self.assertFalse(await queued)
        self.assertFalse(second_ran)

    async def test_pause_during_pacing_sleep_drops_command(self) -> None:
        gate = Open3eCommandGate(min_interval=0.2)
        sent: list[int] = []

        async def send(tag: int) -> None:
            sent.append(tag)

        # First command primes ``__last_send`` so the second one has to wait.
        self.assertTrue(await gate.async_send(lambda: send(0)))

        task = asyncio.create_task(gate.async_send(lambda: send(1)))
        await asyncio.sleep(0.05)  # now inside the pacing sleep
        gate.pause()

        self.assertFalse(await task)
        self.assertEqual(sent, [0])

    async def test_send_exception_propagates_but_gate_stays_usable(self) -> None:
        gate = Open3eCommandGate(min_interval=0)

        async def boom() -> None:
            raise RuntimeError("nope")

        with self.assertRaises(RuntimeError):
            await gate.async_send(boom)

        ran = False

        async def ok() -> None:
            nonlocal ran
            ran = True

        self.assertTrue(await gate.async_send(ok))
        self.assertTrue(ran)


if __name__ == "__main__":
    unittest.main()
