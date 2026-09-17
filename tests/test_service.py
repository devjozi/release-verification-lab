from __future__ import annotations

import unittest

from src.service import health_payload


class HealthPayloadTests(unittest.TestCase):
    def test_health_contract_is_stable(self) -> None:
        self.assertEqual(
            health_payload(),
            {"status": "ok", "service": "release-verification-lab"},
        )


if __name__ == "__main__":
    unittest.main()
