import unittest

from tests.setup import test


class TestLocality(unittest.TestCase):
    def test_locality_01(self):
        self.assertEqual(
            test("""5 miles North of Mason off Hwy 386."""),
            [
                {
                    "locality": "5 miles North of Mason off Hwy 386.",
                    "trait": "locality",
                    "start": 0,
                    "end": 35,
                }
            ],
        )

    def test_locality_02(self):
        self.assertEqual(
            test(
                """
                Tunkhannock Twp. Pocono Pines Quadrangle. Mud Run, Stonecrest Park,.16
                miles SSW of Long Pond, PA. Headwaters wetland of Indiana Mountains
                Lake.
                """
            ),
            [
                {
                    "locality": (
                        "Tunkhannock Twp. Pocono Pines Quadrangle. Mud Run, Stonecrest "
                        "Park,.16 miles SSW of Long Pond, PA. Headwaters wetland of "
                        "Indiana Mountains Lake."
                    ),
                    "trait": "locality",
                    "start": 0,
                    "end": 144,
                }
            ],
        )

    def test_locality_03(self):
        self.assertEqual(
            test("""; files. purple."""),
            [],
        )

    def test_locality_04(self):
        self.assertEqual(
            test("""(Florida's Turnpike)"""),
            [
                {
                    "locality": "Florida's Turnpike",
                    "trait": "locality",
                    "start": 0,
                    "end": 19,
                }
            ],
        )
