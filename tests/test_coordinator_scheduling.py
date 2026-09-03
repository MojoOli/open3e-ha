"""Tests for the coordinator's per-cycle refresh selection.

Run with the standard-library test runner (``scripts/test`` /
``python -m unittest``); a Home Assistant install must be importable because the
package ``__init__`` pulls in ``homeassistant`` modules.
"""

from __future__ import annotations

import math
import unittest

from custom_components.open3e.coordinator import (
    MAX_DATAPOINTS_PER_REQUEST,
    CoordinatorEndpoint,
    select_due_features,
)

# A realistic wall-clock base; ``should_refresh`` compares against ``time.time()``
# and relies on the never-refreshed sentinel (-1) being far in the past.
BASE = 1_700_000_000.0


def _endpoints(
        spec: list[tuple[int, int, int]],
        last_refresh: dict[tuple[int, int], float] | None = None,
) -> dict[tuple[int, int], CoordinatorEndpoint]:
    """Build an endpoint map from ``(device_id, feature_id, refresh_interval)``."""
    last_refresh = last_refresh or {}
    endpoints: dict[tuple[int, int], CoordinatorEndpoint] = {}
    for device_id, feature_id, interval in spec:
        endpoint = CoordinatorEndpoint(refresh_interval=interval)
        if (device_id, feature_id) in last_refresh:
            endpoint.update_last_refresh(last_refresh[(device_id, feature_id)])
        endpoints[(device_id, feature_id)] = endpoint
    return endpoints


class CoordinatorEndpointTest(unittest.TestCase):
    def test_fresh_endpoint_is_always_due(self) -> None:
        endpoint = CoordinatorEndpoint(refresh_interval=10)
        self.assertEqual(endpoint.last_refresh, -1)
        self.assertTrue(endpoint.should_refresh(now=BASE))

    def test_not_due_until_interval_minus_slack(self) -> None:
        endpoint = CoordinatorEndpoint(refresh_interval=10)
        endpoint.update_last_refresh(BASE)
        self.assertFalse(endpoint.should_refresh(BASE + 5.0))
        self.assertTrue(endpoint.should_refresh(BASE + 9.6))


class SelectDueFeaturesTest(unittest.TestCase):
    def test_groups_due_features_by_device_and_skips_not_due(self) -> None:
        endpoints = _endpoints(
            [(0x680, 1, 5), (0x680, 2, 5), (0x684, 9, 5)],
            last_refresh={(0x680, 2): BASE},
        )
        selected = select_due_features(endpoints, now=BASE + 1.0)
        self.assertEqual(selected, {0x680: [1], 0x684: [9]})

    def test_returns_empty_when_nothing_due(self) -> None:
        endpoints = _endpoints([(0x680, 1, 5)], last_refresh={(0x680, 1): BASE})
        self.assertEqual(select_due_features(endpoints, now=BASE + 2.0), {})

    def test_caps_per_device_and_serves_stalest_first(self) -> None:
        spec = [(0x680, fid, 5) for fid in range(30)]
        # Give every endpoint a distinct staleness: feature 0 oldest ... 29 newest.
        last_refresh = {(0x680, fid): BASE + fid for fid in range(30)}
        endpoints = _endpoints(spec, last_refresh=last_refresh)

        selected = select_due_features(endpoints, now=BASE + 1000.0)

        self.assertEqual(len(selected[0x680]), MAX_DATAPOINTS_PER_REQUEST)
        # The stalest MAX_DATAPOINTS_PER_REQUEST features, in staleness order.
        self.assertEqual(selected[0x680], list(range(MAX_DATAPOINTS_PER_REQUEST)))

    def test_each_device_gets_its_own_cap(self) -> None:
        spec = (
            [(0x680, fid, 5) for fid in range(25)]
            + [(0x684, fid, 5) for fid in range(25)]
        )
        selected = select_due_features(_endpoints(spec), now=BASE)
        self.assertEqual(len(selected[0x680]), MAX_DATAPOINTS_PER_REQUEST)
        self.assertEqual(len(selected[0x684]), MAX_DATAPOINTS_PER_REQUEST)

    def test_no_endpoint_starves_across_cycles(self) -> None:
        """Every endpoint is refreshed even when far more than the cap is due."""
        count = 30
        endpoints = _endpoints([(0x680, fid, 5) for fid in range(count)])

        now = BASE
        first_served_at: dict[int, float] = {}
        for _ in range(20):
            now += 5.0
            selected = select_due_features(endpoints, now=now)
            for feature_id in selected.get(0x680, []):
                endpoints[(0x680, feature_id)].update_last_refresh(now)
                first_served_at.setdefault(feature_id, now)

        self.assertEqual(set(first_served_at), set(range(count)))
        max_cycles = math.ceil(count / MAX_DATAPOINTS_PER_REQUEST)
        self.assertLessEqual(max(first_served_at.values()) - BASE, 5.0 * max_cycles)

    def test_mixed_intervals_no_endpoint_starves(self) -> None:
        """Fast and slow endpoints on one device all get served; slow ones
        stop consuming slots once refreshed."""
        spec = (
            [(0x680, fid, 5) for fid in range(25)]
            + [(0x680, 100 + fid, 60) for fid in range(10)]
        )
        endpoints = _endpoints(spec)

        now = BASE
        served: set[int] = set()
        for _ in range(30):
            now += 5.0
            for feature_id in select_due_features(endpoints, now=now).get(0x680, []):
                endpoints[(0x680, feature_id)].update_last_refresh(now)
                served.add(feature_id)

        self.assertEqual(served, {fid for _, fid, _ in spec})

    def test_steady_state_staleness_is_bounded(self) -> None:
        count = 30
        endpoints = _endpoints([(0x680, fid, 5) for fid in range(count)])

        now = BASE
        for _ in range(40):  # warm up past the initial burst
            now += 5.0
            for feature_id in select_due_features(endpoints, now=now).get(0x680, []):
                endpoints[(0x680, feature_id)].update_last_refresh(now)

        worst_staleness = max(now - ep.last_refresh for ep in endpoints.values())
        max_cycles = math.ceil(count / MAX_DATAPOINTS_PER_REQUEST)
        self.assertLessEqual(worst_staleness, 5.0 * max_cycles)


if __name__ == "__main__":
    unittest.main()
