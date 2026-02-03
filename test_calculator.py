"""
Unit tests for RectangularBeam calculator
Tests based on ACI 318 Example 4-1 (Imperial) and 4-1M (SI)
"""

import unittest
import math
from calculator import RectangularBeam


class TestRectangularBeamImperial(unittest.TestCase):
    """Tests for Imperial unit calculations (Example 4-1)."""
    
    def setUp(self):
        """Set up beam with Example 4-1 values."""
        self.beam = RectangularBeam(
            b=12.0,
            h=20.0,
            d=17.5,
            fc=4000.0,
            fy=60000.0,
            n_bars=4,
            bar_area=0.79,  # 4 x No. 8 bars
            unit_system="imperial"
        )
        self.results = self.beam.calculate_mn()
    
    def test_steel_area(self):
        """Test As = n_bars * bar_area."""
        expected_As = 4 * 0.79  # 3.16 in2
        self.assertAlmostEqual(self.results["As"], expected_As, places=2)
    
    def test_stress_block_depth_a(self):
        """Test a = (As * fy) / (0.85 * fc * b)."""
        # a = (3.16 * 60000) / (0.85 * 4000 * 12) = 4.647 in
        self.assertAlmostEqual(self.results["a"], 4.647, delta=0.01)
    
    def test_neutral_axis_depth_c(self):
        """Test c = a / beta1."""
        # c = 4.647 / 0.85 = 5.467 in
        expected_c = self.results["a"] / 0.85
        self.assertAlmostEqual(self.results["c"], expected_c, delta=0.01)
    
    def test_nominal_moment(self):
        """Test Mn calculation."""
        # Mn = As * fy * (d - a/2) / 12000 k-ft
        # Mn = 3.16 * 60000 * (17.5 - 4.647/2) / 12000 = 239.79 k-ft
        self.assertAlmostEqual(self.results["Mn_display"], 239.79, delta=0.5)
    
    def test_tension_controlled(self):
        """Test that beam is tension controlled (epsilon_t >= 0.005)."""
        self.assertGreaterEqual(self.results["epsilon_t"], 0.005)
        self.assertEqual(self.results["phi"], 0.9)
    
    def test_yield_check(self):
        """Test that steel yields."""
        self.assertTrue(self.results["yield_check"])
    
    def test_minimum_steel_check(self):
        """Test minimum steel area calculation."""
        # As_min for fc=4000, fy=60000, b=12, d=17.5
        As_min = self.results["As_min"]
        self.assertGreater(As_min, 0)
        self.assertTrue(self.results["as_check"])  # As >= As_min


class TestRectangularBeamSI(unittest.TestCase):
    """Tests for SI unit calculations (Example 4-1M)."""
    
    def setUp(self):
        """Set up beam with Example 4-1M values."""
        self.beam = RectangularBeam(
            b=250.0,
            h=565.0,
            d=500.0,
            fc=20.0,
            fy=420.0,
            n_bars=3,
            bar_area=510.0,  # 3 x 510 mm2 bars
            unit_system="si"
        )
        self.results = self.beam.calculate_mn()
    
    def test_steel_area(self):
        """Test As = n_bars * bar_area."""
        expected_As = 3 * 510  # 1530 mm2
        self.assertAlmostEqual(self.results["As"], expected_As, places=0)
    
    def test_stress_block_depth_a(self):
        """Test a = (As * fy) / (0.85 * fc * b)."""
        # a = (1530 * 420) / (0.85 * 20 * 250) = 151.76 mm
        self.assertAlmostEqual(self.results["a"], 151.76, delta=1.0)
    
    def test_yield_check(self):
        """Test that steel yields."""
        self.assertTrue(self.results["yield_check"])
    
    def test_minimum_steel_check(self):
        """Test minimum steel area calculation for SI."""
        As_min = self.results["As_min"]
        self.assertGreater(As_min, 0)


class TestBeta1Calculation(unittest.TestCase):
    """Tests for beta1 calculation based on fc."""
    
    def test_beta1_low_fc_imperial(self):
        """Beta1 = 0.85 for fc <= 4000 psi."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=4000, fy=60000,
            n_bars=4, bar_area=0.79, unit_system="imperial"
        )
        self.assertEqual(beam.beta1, 0.85)
    
    def test_beta1_high_fc_imperial(self):
        """Beta1 = 0.65 for fc >= 8000 psi."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=8000, fy=60000,
            n_bars=4, bar_area=0.79, unit_system="imperial"
        )
        self.assertEqual(beam.beta1, 0.65)
    
    def test_beta1_mid_fc_imperial(self):
        """Beta1 interpolated for 4000 < fc < 8000 psi."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=6000, fy=60000,
            n_bars=4, bar_area=0.79, unit_system="imperial"
        )
        # beta1 = 0.85 - 0.05 * (6000 - 4000) / 1000 = 0.75
        self.assertAlmostEqual(beam.beta1, 0.75, places=2)
    
    def test_beta1_override(self):
        """Test that beta1 can be overridden."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=4000, fy=60000,
            n_bars=4, bar_area=0.79, beta1=0.70, unit_system="imperial"
        )
        self.assertEqual(beam.beta1, 0.70)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases."""
    
    def test_single_bar(self):
        """Test with single bar."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=4000, fy=60000,
            n_bars=1, bar_area=0.79, unit_system="imperial"
        )
        results = beam.calculate_mn()
        self.assertEqual(results["As"], 0.79)
    
    def test_custom_epsilon_cu(self):
        """Test with custom ultimate concrete strain."""
        beam = RectangularBeam(
            b=12, h=20, d=17.5, fc=4000, fy=60000,
            n_bars=4, bar_area=0.79, epsilon_cu=0.0035, unit_system="imperial"
        )
        self.assertEqual(beam.epsilon_cu, 0.0035)


if __name__ == '__main__':
    unittest.main()
