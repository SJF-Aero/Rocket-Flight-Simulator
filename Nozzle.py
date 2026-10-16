import math
import matplotlib.pyplot as plt
import numpy as np

# constants
G0 = 9.80665
P0 = 101325.0
T0 = 288.15
L = 0.0065
R_air = 287.05

# chamber conditions
Pc = 3.0e6
Tc = 3400.0
gamma = 1.22
R = 355.0

# nozzle geometry
Dt = 0.050
area_ratio = 8.0

# ambient conditions
Pa = 101325.0

# calculate nozzle areas
At = math.pi * Dt ** 2 / 4
Ae = area_ratio * At


# choked mass flow rate
def mass_flow_rate(Pc, Tc, gamma, R, At):
    mdot = (Pc * At * math.sqrt(gamma / (R * Tc)) * (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1))))

    return mdot

# area mach number
def area_mach(M, gamma):
    area_ratio_calculated = ((1 / M) * ((2 / (gamma + 1)) * (1 + ((((gamma - 1) / 2) * M ** 2)))) ** (
                (gamma + 1) / (2 * (gamma - 1))))

    return area_ratio_calculated

# bisection method for finding exit mach number
def find_exit_mach(area_ratio, gamma):
    # M_low will be slightly above 1 (transonic) and I'll give 10.0 for M_high to be generous
    M_low = 1.0001
    M_high = 10.0

    if area_mach(M_high, gamma) < area_ratio:
        raise ValueError("Supersonic Mach solution is outside search range.")

    tolerance = 1e-6

    while (M_high - M_low) > tolerance:
        M_mid = (M_low + M_high) / 2

        area_ratio_calculated = area_mach(M_mid, gamma)

        if area_ratio_calculated < area_ratio:
            M_low = M_mid
        else:
            M_high = M_mid

    return (M_low + M_high) / 2

# finding exit conditions
def exit_conditions(Me, Pc, Tc, gamma, R):
    Te = Tc / (1 + ((gamma - 1) / 2) * Me ** 2)

    Pe = Pc * (1 + ((gamma - 1) / 2) * Me ** 2) ** (-gamma / (gamma - 1))

    # exit speed of sound
    ae = math.sqrt(gamma * R * Te)

    Ve = Me * ae

    return Te, Pe, ae, Ve

def thrust(mdot, Ve, Pe, Pa, Ae):
    momentum_thrust = mdot * Ve
    pressure_thrust = (Pe - Pa) * Ae

    F_thrust = momentum_thrust + pressure_thrust

    return F_thrust

# Performance functions
def specific_impulse(F_thrust, mdot, G0):
    Isp = F_thrust / (mdot * G0)

    return Isp


def characteristic_velocity(Pc, At, mdot):
    c_star = Pc * At / mdot
    return c_star


def thrust_coefficient(F, Pc, At):
    Cf = F / (Pc * At)

    return Cf

# nozzle being overexpanded vs underexpanded
def nozzle_condition(Pe, Pa):
    if Pa == 0:
        return "Underexpanded"

    tolerance = 0.01

    pressure_difference = abs(Pe - Pa) / Pa

    if pressure_difference <= tolerance:
        return "Ideally Expanded"
    elif Pe > Pa:
        return "Underexpanded"
    else:
        return "Overexpanded"

def expansion_ratio_sweep(min_ratio, max_ratio, step, At, gamma, Pc, Tc, R, mdot, Pa):
    area_ratios = []
    exit_machs = []
    exit_pressures = []
    thrust_values = []
    isp_values = []

    for epsilon in np.arange(min_ratio, max_ratio + step, step):
        Ae_sweep = epsilon * At
        Me_sweep = find_exit_mach(epsilon, gamma)

        Te_sweep, Pe_sweep, ae_sweep, Ve_sweep = exit_conditions(Me_sweep, Pc, Tc, gamma, R)

        F_sweep = thrust(mdot, Ve_sweep, Pe_sweep, Pa, Ae_sweep)
        Isp_sweep = specific_impulse(F_sweep, mdot, G0)

        area_ratios.append(epsilon)
        exit_machs.append(Me_sweep)
        exit_pressures.append(Pe_sweep)
        thrust_values.append(F_sweep)
        isp_values.append(Isp_sweep)

    return area_ratios, exit_machs, exit_pressures, thrust_values, isp_values

def validate_inputs(Pc, Tc, gamma, R, Dt, area_ratio, Pa):
    if Pc <= 0:
        raise ValueError("Chamber pressure must be greater than zero.")

    if Tc <= 0:
        raise ValueError("Chamber temperature must be greater than zero.")

    if gamma <= 1:
        raise ValueError("Gamma must be greater than one.")

    if R <= 0:
        raise ValueError("Specific gas constant must be greater than zero.")

    if Dt <= 0:
        raise ValueError("Throat diameter must be greater than zero.")

    if area_ratio <= 1:
        raise ValueError("Nozzle area ratio must be greater than one.")

    if Pa < 0:
        raise ValueError("Ambient pressure cannot be negative.")

#ambient pressure as a function of altitude
def ambient_pressure(h):
    if h < 0 or h > 10000:
        raise ValueError("This nozzle altitude sweep supports 0 to 10,000 m only.")
    earth_radius = 6356766.0
    H = earth_radius * h / (earth_radius + h)
    Pa = P0 * (1 - (L * H) / T0) ** (G0 / (R_air * L))

    return Pa

if __name__ == "__main__":
    validate_inputs(Pc, Tc, gamma, R, Dt, area_ratio, Pa)
    Me = find_exit_mach(area_ratio, gamma)
    Te, Pe, ae, Ve = exit_conditions(Me, Pc, Tc, gamma, R)
    mdot = mass_flow_rate(Pc, Tc, gamma, R, At)
    F = thrust(mdot, Ve, Pe, Pa, Ae)
    Isp = specific_impulse(F, mdot, G0)
    c_star = characteristic_velocity(Pc, At, mdot)
    Cf = thrust_coefficient(F, Pc, At)
    condition = nozzle_condition(Pe, Pa)

    print("Throat Area:", At, "m^2.")
    print("Exit Area:", Ae, "m^2")
    print("Mass Flow Rate:", mdot, "kg/s")
    print("Exit Mach Number:", Me)
    print("Exit Temperature:", Te, "K")
    print("Exit Pressure", Pe, "Pa")
    print("Exit speed of sound:", ae, "m/s")
    print("Exit Velocity:", Ve, "m/s.")
    print("Thrust:", F, "N")
    print("Specific Impulse:", Isp, "s")
    print("Characteristic Velocity:", c_star, "m/s")
    print("Thrust Coefficient:", Cf)
    print("Nozzle Condition:", condition)

    #parameter sweep
    altitudes = []
    ambient_pressures = []
    altitude_thrust_values = []
    altitude_isp_values = []
    altitude_nozzle_conditions = []
    optimization_altitudes = []
    optimal_area_ratios = []
    optimal_thrust_values = []

    area_ratios, exit_machs, exit_pressures, thrust_values, isp_values = expansion_ratio_sweep(2.0, 30.0, 0.01, At, gamma, Pc, Tc, R, mdot, Pa)

    max_thrust = max(thrust_values)
    max_index = thrust_values.index(max_thrust)
    optimal_area_ratio = area_ratios[max_index]

    print("Maximum Thrust:", max_thrust, "N")
    print("Optimal Expansion Ratio:", round(optimal_area_ratio, 2))

    plt.figure(figsize=(14, 11), layout="constrained")
    plt.subplot(4, 2, 1)
    plt.plot(area_ratios, thrust_values)
    plt.xlabel("Expansion Ratio")
    plt.ylabel("Thrust (N)")
    plt.title("Thrust vs Expansion Ratio", fontsize=10)
    plt.grid()

    plt.subplot(4, 2, 2)
    plt.plot(area_ratios, exit_pressures)
    plt.axhline(y=Pa, linestyle="--", label="Sea-Level Ambient Pressure")
    plt.xlabel("Expansion Ratio")
    plt.ylabel("Exit Pressure (Pa)")
    plt.title("Exit Pressure vs Expansion Ratio", fontsize=10)
    plt.grid()
    plt.legend()

    plt.subplot(4, 2, 3)
    plt.plot(area_ratios, isp_values)
    plt.xlabel("Expansion Ratio")
    plt.ylabel("Specific Impulse (s)")
    plt.title("Specific Impulse vs Expansion Ratio", fontsize=10)
    plt.grid()

    for altitude in np.arange(0, 10001, 100):
        Pa_altitude = ambient_pressure(altitude)

        F_altitude = thrust(mdot, Ve, Pe, Pa_altitude, Ae)
        Isp_altitude = specific_impulse(F_altitude, mdot, G0)
        condition_altitude = nozzle_condition(Pe, Pa_altitude)

        altitudes.append(altitude)
        ambient_pressures.append(Pa_altitude)
        altitude_thrust_values.append(F_altitude)
        altitude_isp_values.append(Isp_altitude)
        altitude_nozzle_conditions.append(condition_altitude)

    pressure_differences = []

    for Pa_altitude in ambient_pressures:
        pressure_difference = abs(Pe - Pa_altitude)
        pressure_differences.append(pressure_difference)

    min_difference = min(pressure_differences)
    ideal_index = pressure_differences.index(min_difference)
    ideal_altitude = altitudes[ideal_index]

    print("Ideal Expansion Altitude:", ideal_altitude, "m")

    for altitude, condition_altitude in zip(altitudes, altitude_nozzle_conditions):
        if condition_altitude == "Ideally Expanded":
            print("Ideally Expanded at:", altitude, "m")

    ideal_indices = [i for i, value in enumerate(altitude_nozzle_conditions) if value == "Ideally Expanded"]
    if ideal_indices:
        first_ideal_index = ideal_indices[0]
        last_ideal_index = ideal_indices[-1]
        print("Overexpanded below:", altitudes[first_ideal_index], "m")
        print("Ideal Expansion Range:", altitudes[first_ideal_index], "to", altitudes[last_ideal_index], "m")
        print("Underexpanded above:", altitudes[last_ideal_index], "m")
    else:
        print("No sampled altitude meets the 1% ideal-expansion tolerance.")

    for altitude in np.arange(0, 10001, 100):
        Pa_altitude = ambient_pressure(altitude)

        area_ratios_alt, exit_machs_alt, exit_pressures_alt, thrust_values_alt, isp_values_alt = expansion_ratio_sweep(2.0, 30.0, 0.01, At, gamma, Pc, Tc, R, mdot, Pa_altitude)

        max_thrust_altitude = max(thrust_values_alt)
        max_index_altitude = thrust_values_alt.index(max_thrust_altitude)
        optimal_area_ratio_altitude = area_ratios_alt[max_index_altitude]

        optimization_altitudes.append(altitude)
        optimal_area_ratios.append(optimal_area_ratio_altitude)
        optimal_thrust_values.append(max_thrust_altitude)

    plt.subplot(4, 2, 4)
    plt.plot(altitudes, altitude_thrust_values)
    plt.xlabel("Altitude (m)")
    plt.ylabel("Thrust (N)")
    plt.title("Thrust vs Altitude", fontsize=10)
    plt.grid()

    plt.subplot(4, 2, 5)
    plt.plot(altitudes, altitude_thrust_values, label = f"Fixed Expansion Ratio ({area_ratio})")
    plt.plot(optimization_altitudes, optimal_thrust_values, label = "Optimized Expansion Ratio")
    plt.xlabel("Altitude (m)")
    plt.ylabel("Thrust (N)")
    plt.title("Fixed vs Optimized Nozzle Thrust", fontsize=10)
    plt.grid()
    plt.legend()

    thrust_losses = []
    thrust_loss_percentages = []

    for fixed_thrust, optimal_thrust in zip(altitude_thrust_values, optimal_thrust_values):
        thrust_loss = optimal_thrust - fixed_thrust
        thrust_loss_percentage = (thrust_loss / optimal_thrust) * 100

        thrust_losses.append(thrust_loss)
        thrust_loss_percentages.append(thrust_loss_percentage)

    max_thrust_loss_percentage = max(thrust_loss_percentages)
    max_loss_index = thrust_loss_percentages.index(max_thrust_loss_percentage)
    max_loss_altitude = altitudes[max_loss_index]

    print("\n--- V2.2 Design Summary ---")
    print("Fixed Expansion Ratio:", area_ratio)
    print("Sea-Level Thrust:", F, "N")
    print("Sea-Level Specific Impulse:", Isp, "s")
    print("Sea-Level Nozzle Condition:", condition)
    print("Sea-Level Optimal Expansion Ratio:", round(optimal_area_ratio, 2))
    print("Ideal Expansion Altitude:", ideal_altitude, "m")
    if ideal_indices:
        print("Ideal Expansion Range:", altitudes[first_ideal_index], "to", altitudes[last_ideal_index], "m")
    else:
        print("Ideal Expansion Range: not found in sampled altitudes")
    print("Optimal Expansion Ratio at 10 km:", round(optimal_area_ratios[-1], 2))
    print("Maximum Fixed-Nozzle Thrust Loss:", round(max_thrust_loss_percentage, 3), "%")
    print("Maximum Loss Altitude:", max_loss_altitude, "m")

    optimal_exit_pressure = exit_pressures[max_index]
    pressure_error = abs(optimal_exit_pressure - Pa) / Pa * 100

    print("\n--- V2.2 VALIDATION---")
    print("Sea-Level Ambient Pressure:", Pa, "Pa")
    print("Exit Pressure at Optimal Expansion Ratio:", optimal_exit_pressure, "Pa")
    print("Pressure Difference:", pressure_error, "%")

    plt.subplot(4, 2, 6)
    plt.plot(altitudes, thrust_loss_percentages)
    plt.xlabel("Altitude (m)")
    plt.ylabel("Thrust loss (%)")
    plt.title("Fixed Nozzle Performance Penalty vs Altitude", fontsize=10)
    plt.grid()

    plt.subplot(4, 2, 7)
    plt.plot(optimization_altitudes, optimal_area_ratios)
    plt.xlabel("Altitude (m)")
    plt.ylabel("Optimal Expansion Ratio")
    plt.title("Optimal Expansion Ratio vs Altitude", fontsize=10)
    plt.grid()
    plt.show()
