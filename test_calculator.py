import unittest
from calculator import RectangularBeam

class TestRectangularBeam(unittest.TestCase):
    def test_example_4_19a(self):
        # Example 4-19a inputs
        # f'c = 4000 psi
        # fy = 60000 psi
        # 4 No. 8 bars -> As = 3.16 in^2 (approx 0.79 * 4)
        # b = 12 in
        # d = 20 - 2.5 = 17.5 in
        
        beam = RectangularBeam(
            width=12.0,
            effective_depth=17.5,
            f_c=4000.0,
            f_y=60000.0,
            rebar_area=3.16 # 4 * 0.79
        )
        
        results = beam.calculate_mn()
        
        # Expected results (approximate from standard texts)
        # a = (3.16 * 60) / (0.85 * 4 * 12) = 189.6 / 40.8 = 4.647 in
        # Mn = 3.16 * 60 * (17.5 - 4.647/2)
        # Mn = 189.6 * (17.5 - 2.3235) = 189.6 * 15.1765 = 2877.46 k-in
        # Mn_kft = 2877.46 / 12 = 239.79 k-ft
        
        print(f"Calculated a: {results['a']}")
        print(f"Calculated Mn (k-ft): {results['Mn_kft']}")
        
        self.assertAlmostEqual(results['a'], 4.647, delta=0.01)
        self.assertAlmostEqual(results['Mn_kft'], 239.79, delta=0.5)
        self.assertGreaterEqual(results['epsilon_t'], 0.005) # Tension controlled
        self.assertEqual(results['phi'], 0.9)

if __name__ == '__main__':
    unittest.main()
