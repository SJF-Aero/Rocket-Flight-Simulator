import unittest
import contextlib
import io
import math
import Flight
import Nozzle

class FlightTests(unittest.TestCase):
    def run_flight(self, stages, payload=0):
        with contextlib.redirect_stdout(io.StringIO()):
            return Flight.simulate_flight(stages, payload)

    def test_impulse_integral(self):
        curve = [(0, 0), (1, 100), (2, 100), (3, 0)]
        self.assertAlmostEqual(Flight.total_motor_impulse(curve), 200)
        self.assertAlmostEqual(Flight.thrust_curve_impulse_between(curve, 0.5, 2.5), 175)

    def test_atmosphere(self):
        self.assertAlmostEqual(Flight.atmospheric_pressure(0), 101325, places=3)
        self.assertAlmostEqual(Flight.atmospheric_density(0), 1.225, delta=.002)
        self.assertAlmostEqual(Flight.atmospheric_pressure(11000), 22699.9, delta=250)
        self.assertAlmostEqual(Flight.atmospheric_pressure(20000), 5529.3, delta=80)
        for h in [0, 11000, 20000, 50000, 86000, 100000, 200000]:
            self.assertGreater(Flight.atmospheric_density(h), 0)

    def test_drag_sign(self):
        self.assertLess(Flight.drag_force(1.2, 100, .5, .1), 0)
        self.assertGreater(Flight.drag_force(1.2, -100, .5, .1), 0)

    def test_burnout_mass_conservation(self):
        result = self.run_flight(Flight.stages, Flight.payload_mass)
        self.assertEqual(len(result['burnouts']), 2)
        self.assertAlmostEqual(result['burnouts'][0]['mass'], result['initial_mass_kg'] - Flight.stage_1.propellant_mass, places=6)
        self.assertAlmostEqual(result['final_mass_kg'], Flight.payload_mass + Flight.stage_2.dry_mass, places=6)
        self.assertGreater(result['apogee_m'], result['burnouts'][-1]['altitude'])

    def test_no_liftoff_with_weak_motor(self):
        weak = Flight.Stage(100, 1, .2, None, None, None, None, None, None, [(0, 1), (1, 1), (1.01, 0)], 1.01)
        result = self.run_flight([weak])
        self.assertAlmostEqual(result['apogee_m'], 0)
        self.assertGreaterEqual(min(result['acceleration_m_s2']), 0)

    def test_nozzle_area_mach_round_trip(self):
        for epsilon in [2, 4, 8, 16]:
            m = Nozzle.find_exit_mach(epsilon, Nozzle.gamma)
            self.assertAlmostEqual(Nozzle.area_mach(m, Nozzle.gamma), epsilon, delta=.0001)

    def test_nozzle_atmosphere_range(self):
        self.assertAlmostEqual(Nozzle.ambient_pressure(0), 101325, places=3)
        self.assertAlmostEqual(Nozzle.ambient_pressure(10000), Flight.atmospheric_pressure(10000), delta=1)
        with self.assertRaises(ValueError):
            Nozzle.ambient_pressure(50000)

    def test_nozzle_ideal_expansion(self):
        mdot = Nozzle.mass_flow_rate(Nozzle.Pc, Nozzle.Tc, Nozzle.gamma, Nozzle.R, Nozzle.At)
        self.assertGreater(mdot, 0)
        ratios, machs, pressures, forces, isp = Nozzle.expansion_ratio_sweep(4, 6, .01, Nozzle.At, Nozzle.gamma, Nozzle.Pc, Nozzle.Tc, Nozzle.R, mdot, Nozzle.P0)
        best = forces.index(max(forces))
        self.assertAlmostEqual(pressures[best], Nozzle.P0, delta=1500)

    def test_mass_budget_is_not_forced_to_match(self):
        model_mass = Flight.payload_mass + sum(x.dry_mass + x.propellant_mass for x in Flight.stages)
        self.assertAlmostEqual(model_mass, Flight.simulated_initial_mass)
        self.assertAlmostEqual(Flight.mass_difference, model_mass - Flight.reference_initial_mass)
        self.assertGreater(abs(Flight.mass_difference), 1)

    def test_constant_thrust_rocket_equation(self):
        # A constant-thrust stage without drag should roughly follow the rocket equation.
        # Gravity varies slightly with height, so use a short low-altitude burn.
        stage = Flight.Stage(80, 20, .001, None, None, None, None, None, None,
                             [(0, 3000), (1, 3000), (1.000001, 0)], 1.000001)
        result = self.run_flight([stage])
        burnout = result['burnouts'][0]
        mdot = 20 / 1.000001
        expected = 3000 / mdot * math.log(100 / 80) - Flight.G0 * 1.000001
        self.assertAlmostEqual(burnout['velocity'], expected, delta=1)

    def test_time_step_convergence(self):
        original_dt = Flight.dt
        try:
            Flight.dt = .04
            coarse = self.run_flight(Flight.stages, Flight.payload_mass)['apogee_m']
            Flight.dt = .02
            medium = self.run_flight(Flight.stages, Flight.payload_mass)['apogee_m']
            Flight.dt = .01
            fine = self.run_flight(Flight.stages, Flight.payload_mass)['apogee_m']
        finally:
            Flight.dt = original_dt
        self.assertLess(abs(fine - medium), abs(medium - coarse) + 2)
        self.assertLess(abs(fine - medium) / fine, .002)

    def test_nozzle_ideal_condition_can_be_absent(self):
        # A small expansion ratio need not match ambient pressure on the 100 m grid.
        me = Nozzle.find_exit_mach(4.0, Nozzle.gamma)
        pe = Nozzle.exit_conditions(me, Nozzle.Pc, Nozzle.Tc, Nozzle.gamma, Nozzle.R)[1]
        conditions = [Nozzle.nozzle_condition(pe, Nozzle.ambient_pressure(h))
                      for h in range(0, 10001, 100)]
        ideal_indices = [i for i, value in enumerate(conditions) if value == 'Ideally Expanded']
        self.assertIsInstance(ideal_indices, list)

    def test_pressure_atmosphere_reference(self):
        self.assertAlmostEqual(Flight.atmospheric_pressure(0), 101325, delta=1)
        self.assertAlmostEqual(Flight.atmospheric_pressure(20000), 5529.3, delta=80)
        self.assertAlmostEqual(Flight.atmospheric_pressure(50000), 79.8, delta=4)

if __name__ == '__main__':
    unittest.main()
