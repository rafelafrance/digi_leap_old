import unittest

from tests.setup import test


class TestLocality(unittest.TestCase):
    def test_locality_01(self):
        """It gets a locality notation."""
        self.assertEqual(
            test("""5 miles North of Mason off Hwy 386."""),
            [
                {
                    "locality": "5 miles North of Mason off Hwy 386",
                    "trait": "locality",
                    "start": 0,
                    "end": 34,
                }
            ],
        )

    def test_locality_02(self):
        self.assertEqual(
            test("""5 miles North of Mason off Hwy 386."""),
            [
                {
                    "locality": "5 miles North of Mason off Hwy 386",
                    "trait": "locality",
                    "start": 0,
                    "end": 34,
                }
            ],
        )
