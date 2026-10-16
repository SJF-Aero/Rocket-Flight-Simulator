# Rocket Flight & Propulsion Simulator

A Python-based engineering project modeling the flight dynamics of a two-stage sounding rocket and the performance of a converging-diverging rocket nozzle.

The project combines numerical simulation, compressible-flow theory, and automated testing to investigate how propulsion characteristics, vehicle mass, aerodynamic forces, and staging affect rocket performance.

## Project Overview

The project consists of two independent simulation tools:

**1. Two-Stage Rocket Flight Simulator (`Flight.py`)**

A one-dimensional vertical flight simulation based on the Terrier Mk12–Improved Orion sounding rocket configuration.

The model incorporates:
- Altitude-dependent atmospheric density and pressure
- Variable gravitational acceleration
- Mach-dependent aerodynamic drag
- Time-dependent motor thrust and propellant consumption
- First-stage separation and second-stage ignition
- Numerical integration of rocket equations of motion
- Flight performance calculations, including apogee and maximum dynamic pressure

**2. Rocket Nozzle Performance Simulator (`Nozzle.py`)**

An ideal, isentropic converging-diverging nozzle model used to evaluate rocket propulsion performance.

The model calculates:
- Choked mass flow rate
- Exit Mach number and thermodynamic properties
- Exhaust velocity
- Thrust and specific impulse
- Characteristic velocity and thrust coefficient
- Nozzle expansion performance across ambient pressures

## Technical Approach

The flight simulator numerically integrates the rocket's equations of motion using a time-stepping method, accounting for changing vehicle mass, atmospheric conditions, thrust, and drag.

The nozzle simulator applies compressible-flow relations and numerical root-finding to determine supersonic exit conditions and estimate ideal nozzle performance.

Both models use simplifying assumptions to isolate key engineering relationships and support further development.

## Verification and Limitations

Automated tests are included in `Test_Flight.py` to evaluate numerical behavior and selected physical relationships.

The flight simulation has also been examined through timestep refinement, comparison with an independent numerical integration method, and sensitivity studies involving alternative motor and mass assumptions.

These checks support numerical consistency but do not establish experimental validation or confirm that all input parameters represent a flight-qualified vehicle.

Current limitations include one-dimensional flight dynamics, simplified aerodynamic modeling, assumed motor parameters, and idealized nozzle flow.

## Documentation

A detailed engineering report is included in **`Technical_Report.pdf`**.

The report covers:
- Mathematical models and governing equations
- Input parameters and modeling assumptions
- Simulation results and performance plots
- Numerical verification and sensitivity analysis
- Model limitations and planned improvements
- References and supporting technical documentation

## Future Development

Planned extensions include:

- Refinement of propulsion and aerodynamic inputs using additional reference data
- Expanded numerical verification and model validation
- CAD development of nozzle geometries
- Manufacturing and physical cold-flow thrust testing
- Comparison of experimental nozzle performance with theoretical predictions

## Technologies and Engineering Concepts

**Programming:** Python

**Engineering:** Rocket propulsion, compressible fluid flow, flight dynamics, numerical methods, aerodynamics, and engineering verification

## Author

Sam Forman  
Aerospace Engineering (Astronautics)  
Arizona State University | Barrett, The Honors College

---

*This project is an educational engineering simulation. Reported performance values are model predictions and should not be interpreted as experimentally validated flight or propulsion data.*
