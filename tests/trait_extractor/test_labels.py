"""Test trait extraction on labels."""
import unittest

from tests.setup import test


class TestLabels(unittest.TestCase):
    """Test trait extraction on labels."""

    def test_label_00(self):
        test(
            """
            PLANTS OF FLORIDA
            Cyperus
            aculeatus
            CHARLOTTE CO.: Prairie / Shell Creek(SFWMD
            property); 0.05 ofUS 17, 1.3 Sof Sam
            Way:
            26° 59’21" N, 81° 57' 35" W.
            Ruderal depression:
            Alan R. Franck 2523
            4 December 2010
            UNIVERSITY OF SOUTH FLORIDA HERBARIUM
        """
        )
