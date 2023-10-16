import unittest

from flora.pylib.traits.habit import Habit
from flora.pylib.traits.part import Part
from tests.setup import small_test


class TestHabit(unittest.TestCase):
    def test_habit_01(self):
        self.assertEqual(
            small_test("Stems often caespitose"),
            [
                Part(
                    part="stem", trait="plant_part", start=0, end=5, type="plant_part"
                ),
                Habit(
                    habit="cespitose",
                    trait="habit",
                    start=12,
                    end=22,
                ),
            ],
        )

    def test_habit_02(self):
        self.assertEqual(
            small_test("Herbs perennial or subshrubs, epiphytic or epilithic."),
            [
                Habit(
                    woodiness="herb",
                    trait="woodiness",
                    start=0,
                    end=5,
                    plant_part="shrub",
                ),
                Habit(
                    plant_duration="perennial",
                    trait="plant_duration",
                    start=6,
                    end=15,
                ),
                Part(
                    part="shrub",
                    trait="plant_part",
                    start=19,
                    end=28,
                    type="plant_part",
                ),
                Habit(
                    habit="epiphytic",
                    trait="habit",
                    start=30,
                    end=39,
                ),
                Habit(
                    habit="epilithic",
                    trait="habit",
                    start=43,
                    end=52,
                ),
            ],
        )
