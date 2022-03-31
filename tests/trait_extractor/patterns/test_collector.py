"""Test collector patterns."""
import unittest

from tests.setup import test


class TestCollector(unittest.TestCase):
    """Test administrative unit patterns."""

    # def test_collector_00(self):
    #     test("""Sarah Nunn and S. Jacobs and R. Mc Elderry 9480""")

    def test_collector_01(self):
        """It gets a county notation."""
        self.assertEqual(
            test("""Sarah Nunn and S. Jacobs and R. Mc Elderry 9480"""),
            [
                {
                    "collector_no": "9480",
                    "collector": ["Sarah Nunn", "S. Jacobs", "R. Mc Elderry"],
                    "trait": "collector",
                    "start": 0,
                    "end": 47,
                }
            ],
        )

    def test_collector_02(self):
        """It does not parse other fields."""
        self.assertEqual(
            test(
                """
                Rhus glabra L. "Smooth Sumac"
                Woodruff Co., Arkansas
                Vicinity of bridge on Hwy 33, ca. 2 mi. S. of the
                town of Gregory; S19, T6N; R3W.
                Det, Edwin B. Smith
                Coll. Marie P. Locke No. 5595
                Date June 29, 1985
                """
            ),
            [
                {
                    "collector_no": "5595",
                    "collector": "Marie P. Locke",
                    "trait": "collector",
                    "start": 155,
                    "end": 184,
                },
                {
                    "label_date": "1985-06-29",
                    "trait": "label_date",
                    "start": 185,
                    "end": 203,
                },
                {
                    "us_state": "Arkansas",
                    "us_county": "Woodruff",
                    "trait": "admin_unit",
                    "start": 30,
                    "end": 52,
                },
            ],
        )


#     def test_collector_04(self):
#         """It handles a bad name."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 APPALACHIAN STATE UNIVERSITY HERBARIUM
#                 PLANTS OF NORTH CAROLINA
#                 Collected by _Wayne.. Hutchins.
#                 """
#                 )
#             ),
#             [Trait(col_name="Hutchins", start=65, end=95)],
#         )
#
#     def test_collector_05(self):
#         """It handles initials differently."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 x
#                 e
#                 Coll. Marie P. Locke No. 5595
#                 """
#                 )
#             ),
#             [Trait(col_name="Marie P. Locke", col_no="5595", start=5, end=34)],
#         )
#
#     def test_collector_06(self):
#         """It handles random words matching names."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 Woodsia obtusa (Sprengel) Torrey
#                 Dry hardwood slope 3 miles south of
#                 Isothermal Community College.
#                 Altitude 960 ft.
#                 Date 6/9/75
#                 Collected by _Wayne.. Hutchins.
#                 """
#                 )
#             ),
#             [Trait(col_name="Hutchins", start=129, end=159)],
#         )
#
#     def test_collector_07(self):
#         """It handles more random words matching names."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 Vermont
#                 Three plants only on South side of 189, These are the
#                 first plants of this species seen on the Interstate between.
#                 """
#                 )
#             ),
#             [],
#         )
#
#     def test_collector_08(self):
#         """It handles more random words matching names."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 PRINGLE HERBARIUM
#                 DEPT. OF BOTANY @ UNIVERSITY OF VERMONT
#                 Campyloneuron repens (Auble.) C.Pres]
#                 Costa Rica, Cartago Prov. Valle de La Estrella. Road
#                 between Estrella and Vara de Roble. 1600m. Steep canyon
#                 with stream on east flowing into Rio Empalme,
#                 ex Herb Hugo Churchill
#                 3466
#                 Hugo Churchill Feb, 5, 1980
#                 """
#                 )
#             ),
#             [Trait(col_name="Hugo Churchill", start=280, end=294)],
#         )
#
#     def test_collector_09(self):
#         """It parses with noise at the start of a line."""
#         self.assertEqual(
#             COLLECTOR.parse("[| WILLIAM DOUGLAS COUNTRYMAN"),
#             [Trait(col_name="WILLIAM DOUGLAS COUNTRYMAN", start=0, end=29)],
#         )
#
#     def test_collector_10(self):
#         """It handles more random words matching names."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 WGS84. Flevation: 1,524 m (5000 ft) - 1530 m (5020 ft)
#                 Andrew Jenkins 427 93/2009
#                 """
#                 )
#             ),
#             [Trait(col_name="Andrew Jenkins", col_no="427", start=56, end=74)],
#         )
#
#     def test_collector_11(self):
#         """It parses name suffixes."""
#         self.assertEqual(
#             COLLECTOR.parse("Coll. E. E. Dale, Jr. No. 6061"),
#             [Trait(col_name="E. E. Dale Jr", col_no="6061", start=0, end=30)],
#         )
#
#     def test_collector_12(self):
#         """It removes noise."""
#         self.assertEqual(
#             COLLECTOR.parse("""Collected by ....... Marie. HACKS.......ccccee No."""),
#             [Trait(col_name="Marie. HACKS", start=0, end=46)],
#         )
#
#     def test_collector_13(self):
#         """It parses multi-part collector numbers."""
#         self.assertEqual(
#             COLLECTOR.parse("Coll. Stephen W. Bailey No, SWBII 1)"),
#             [Trait(col_name="Stephen W. Bailey", col_no="SWBII 1", start=0, end=35)],
#         )
#
#     def test_collector_14(self):
#         """It handles newlines between collector and collector number."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 Coll. Marie P. Locke
#
#                 No. 2319
#                 Date September 4, 1977
#                 """
#                 )
#             ),
#             [Trait(col_name="Marie P. Locke", col_no="2319", start=1, end=31)],
#         )
#
#     def test_collector_15(self):
#         """It parses collectors separated by 'with'."""
#         self.assertEqual(
#             COLLECTOR.parse("Sarah Nunn with Angela Brown 7529 20 October 2002 of"),
#             [
#                 Trait(col_name="Sarah Nunn", col_no="7529", start=0, end=33),
#                 Trait(col_name="Angela Brown", start=0, end=33),
#             ],
#         )
#
#     def test_collector_16(self):
#         """It parses collectors separated by 'with'."""
#         self.assertEqual(
#             COLLECTOR.parse(
#                 textwrap.dedent(
#                     """
#                 Collector: Christopher Reid & Sarah Nunn
#                 No.: 2018 Date: 16 May 2001
#                 """
#                 )
#             ),
#             [
#                 Trait(col_name="Christopher Reid", col_no="2018", start=1, end=51),
#                 Trait(col_name="Sarah Nunn", start=1, end=51),
#             ],
#         )
#
#     def test_collector_17(self):
#         """It handles a run-on with the label."""
#         self.assertEqual(
#             COLLECTOR.parse("""ColMrs. Jim Miller No. 736"""),
#             [Trait(col_name="Jim Miller", col_no="736", start=0, end=26)],
#         )
#
#     def test_collector_18(self):
#         """It handles a run-on with the label."""
#         self.assertEqual(
#             COLLECTOR.parse("""Sarah Nunn and Laura Eason 9834"""),
#             [
#                 Trait(col_name="Sarah Nunn", col_no="9834", start=0, end=31),
#                 Trait(col_name="Laura Eason", start=0, end=31),
#             ],
#         )
#
#     def test_collector_19(self):
#         """This failed."""
#         self.assertEqual(
#             COLLECTOR.parse("""George P. Johnson #5689"""),
#             [Trait(col_name="George P. Johnson", col_no="5689", start=0, end=23)],
#         )
