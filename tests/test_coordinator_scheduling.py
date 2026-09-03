"""Tests for the coordinator's per-endpoint refresh scheduling.

Run with the standard-library test runner (``scripts/test`` /
``python -m unittest``); a Home Assistant install must be importable because the
package ``__init__`` pulls in ``homeassistant`` modules.
"""

from __future__ import annotations

import unittest

from custom_components.open3e.coordinator import CoordinatorEndpoint

# A realistic wall-clock base; ``should_refresh`` compares against ``time.time()``
# and relies on the never-refreshed sentinel (-1) being far in the past.
BASE = 1_700_000_000.0


class CoordinatorEndpointTest(unittest.TestCase):
    def test_fresh_endpoint_is_always_due(self) -> None:
        endpoint = CoordinatorEndpoint(refresh_interval=10)
        self.assertTrue(endpoint.should_refresh(now=BASE))

    def test_not_due_until_interval_minus_slack(self) -> None:
        endpoint = CoordinatorEndpoint(refresh_interval=10)
        endpoint.update_last_refresh(BASE)
        self.assertFalse(endpoint.should_refresh(BASE + 5.0))
        self.assertTrue(endpoint.should_refresh(BASE + 9.6))

    def test_due_again_after_a_full_interval(self) -> None:
        endpoint = CoordinatorEndpoint(refresh_interval=5)
        endpoint.update_last_refresh(BASE)
        self.assertTrue(endpoint.should_refresh(BASE + 5.0))


if __name__ == "__main__":
    unittest.main()
