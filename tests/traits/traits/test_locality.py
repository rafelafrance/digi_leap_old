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
                    "locality": "Tunkhannock Twp",
                    "trait": "locality",
                    "start": 0,
                    "end": 15,
                },
                {
                    "locality": "Pocono Pines Quadrangle",
                    "trait": "locality",
                    "start": 17,
                    "end": 40,
                },
                {
                    "locality": "Mud Run, Stonecrest Park",
                    "trait": "locality",
                    "start": 42,
                    "end": 66,
                },
                {
                    "locality": ".16 miles SSW of Long Pond, PA",
                    "trait": "locality",
                    "start": 67,
                    "end": 97,
                },
                {
                    "locality": "Headwaters wetland of Indiana Mountains Lake",
                    "trait": "locality",
                    "start": 99,
                    "end": 143,
                },
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

    def test_locality_05(self):
        self.assertEqual(
            test(
                """
                Wallowa-Whitman National Forest, Forest Service Road 7312.
                """
            ),
            [
                {
                    "locality": "Wallowa-Whitman National Forest",
                    "trait": "locality",
                    "start": 0,
                    "end": 31,
                },
                {"habitat": "forest", "trait": "habitat", "start": 33, "end": 39},
                {
                    "locality": "Service Road 7312.",
                    "trait": "locality",
                    "start": 40,
                    "end": 58,
                },
            ],
        )

    def test_locality_06(self):
        self.assertEqual(
            test("""Sonoran Desert scrub, disturbed trail side. Occasional annual."""),
            [
                {
                    "habitat": "sonoran desert scrub",
                    "trait": "habitat",
                    "start": 0,
                    "end": 20,
                },
                {
                    "locality": "disturbed trail side",
                    "trait": "locality",
                    "start": 22,
                    "end": 42,
                },
                {
                    "plant_duration": "annual",
                    "trait": "plant_duration",
                    "start": 55,
                    "end": 61,
                },
            ],
        )

    def test_locality_07(self):
        self.assertEqual(
            test(
                """
                Pocono Pines Quadrangle. Mud Run, Stonecrest Park,.16 miles SSW of
                Long Pond, PA. Headwaters wetland of Indiana Mountains Lake.
                """
            ),
            [
                {
                    "locality": "Pocono Pines Quadrangle",
                    "trait": "locality",
                    "start": 0,
                    "end": 23,
                },
                {
                    "locality": "Mud Run, Stonecrest Park",
                    "trait": "locality",
                    "start": 25,
                    "end": 49,
                },
                {
                    "locality": ".16 miles SSW of Long Pond, PA",
                    "trait": "locality",
                    "start": 50,
                    "end": 80,
                },
                {
                    "locality": "Headwaters wetland of Indiana Mountains Lake",
                    "trait": "locality",
                    "start": 82,
                    "end": 126,
                },
            ],
        )

    def test_locality_08(self):
        self.assertEqual(
            test(
                """
                Arizona Uppland Sonoran Desert desert scrub, flats.
                Sandy soil Local erecta annual,
                """
            ),
            [
                {
                    "locality": "Arizona Uppland Sonoran Desert desert scrub",
                    "trait": "locality",
                    "start": 0,
                    "end": 43,
                },
                {"habitat": "sandy soil", "trait": "habitat", "start": 52, "end": 62},
                {
                    "plant_duration": "annual",
                    "trait": "plant_duration",
                    "start": 76,
                    "end": 82,
                },
            ],
        )
