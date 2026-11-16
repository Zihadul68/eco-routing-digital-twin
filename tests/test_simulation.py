import unittest
from eco_routing_twin import EcoRoutingDigitalTwin


class SimulationTests(unittest.TestCase):
    def test_rack_layout_and_ids(self):
        sim = EcoRoutingDigitalTwin(seed=1)
        self.assertEqual([r.rack_id for r in sim.racks], [f"RACK-{i:02d}" for i in range(1, 7)])
        self.assertLess(sim.racks[2].crac_proximity_factor, sim.racks[0].crac_proximity_factor)

    def test_reproducible_run(self):
        a = EcoRoutingDigitalTwin(seed=123).run_simulation(steps=5, rps=2, mode="eco")
        b = EcoRoutingDigitalTwin(seed=123).run_simulation(steps=5, rps=2, mode="eco")
        self.assertEqual(a, b)

    def test_output_shape_and_modes(self):
        sim = EcoRoutingDigitalTwin(seed=5)
        rows = sim.run_simulation(steps=4, rps=3, mode="round_robin")
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["mode"], "round_robin")
        self.assertIn("water_usage_lph_proxy", rows[0])

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            EcoRoutingDigitalTwin().run_simulation(mode="unknown")


if __name__ == "__main__":
    unittest.main()
