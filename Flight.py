import math

import Nozzle as nozzle

# Vehicle data are illustrative; see MODEL_NOTES.md for sources and limits.


class Stage:
    def __init__(self, dry_mass, propellant_mass, diameter, Pc, Tc, gamma, R, Dt, area_ratio, thrust_curve=None,
                 burn_time=None):
        self.dry_mass = dry_mass
        self.propellant_mass = propellant_mass
        self.diameter = diameter
        self.Pc = Pc
        self.Tc = Tc
        self.gamma = gamma
        self.R = R
        self.Dt = Dt
        self.area_ratio = area_ratio
        self.thrust_curve = thrust_curve
        self.burn_time = burn_time


# rocket properties
stage_1 = Stage(
    dry_mass=322.0,
    propellant_mass=578.0,
    diameter=0.4572,
    Pc=nozzle.Pc,
    Tc=nozzle.Tc,
    gamma=nozzle.gamma,
    R=nozzle.R,
    Dt=nozzle.Dt,
    area_ratio=nozzle.area_ratio,
    thrust_curve=[
        (0.0, 257500.0),
        (4.39, 257500.0),
        (4.40, 0.0)
    ],
    burn_time=4.40
)

stage_2 = Stage(
    dry_mass=150.0,
    propellant_mass=378.769375439337,
    # Stage 2: Improved Orion
    diameter=0.3556,
    Pc=nozzle.Pc,
    Tc=nozzle.Tc,
    gamma=nozzle.gamma,
    R=nozzle.R,
    Dt=nozzle.Dt,
    area_ratio=nozzle.area_ratio,
    thrust_curve=[
        (0.0, 88964.4),
        (6.0, 88964.4),
        (6.01, 17792.9),
        (23.99, 17792.9),
        (24.0, 0.0)
    ],
    burn_time=24.0
)

stages = [stage_1, stage_2]

# Reference payload: 300 lb
payload_mass = 136.077

reference_vehicle_mass = 2850.0 * 0.45359237
reference_initial_mass = reference_vehicle_mass + payload_mass

simulated_initial_mass = payload_mass + sum(
    stage.dry_mass + stage.propellant_mass
    for stage in stages
)

mass_difference = simulated_initial_mass - reference_initial_mass  # positive means model is heavier



# aerodynamic model
mach_cd_data = [
    (0.0, 0.40),
    (0.5, 0.40),
    (0.8, 0.42),
    (0.9, 0.48),
    (1.0, 0.62),
    (1.1, 0.68),
    (1.2, 0.64),
    (1.5, 0.55),
    (2.0, 0.48),
    (3.0, 0.42),
    (4.0, 0.39),
    (5.0, 0.37)
]

# atmospheric constants
P0 = 101325.0
T0 = 288.15
L = 0.0065
R_air = 287.05
gamma_air = 1.4
G0 = 9.80665
earth_radius = 6356766.0
troposphere_limit = 11000.0
T11 = T0 - L * troposphere_limit
P11 = P0 * (1 - (L * troposphere_limit) / T0) ** (G0 / (R_air * L))
stratosphere_layer_1_limit = 20000.0
stratosphere_layer_2_limit = 32000.0
stratosphere_layer_3_limit = 47000.0
stratosphere_layer_4_limit = 51000.0
mesosphere_layer_1_limit = 71000.0
mesosphere_layer_2_limit = 84852.0
L20_32 = 0.001
L32_47 = 0.0028
T20 = T11
P20 = P11 * math.exp(-G0 * (stratosphere_layer_1_limit - troposphere_limit) / (R_air * T11))
T32 = T20 + L20_32 * (stratosphere_layer_2_limit - stratosphere_layer_1_limit)
P32 = P20 * (T32 / T20) ** (-G0 / (R_air * L20_32))
T47 = T32 + L32_47 * (stratosphere_layer_3_limit - stratosphere_layer_2_limit)
P47 = P32 * (T47 / T32) ** (-G0 / (R_air * L32_47))
T51 = T47
P51 = P47 * math.exp(-G0 * (stratosphere_layer_4_limit - stratosphere_layer_3_limit) / (R_air * T47))
L51_71 = -0.0028
T71 = T51 + L51_71 * (mesosphere_layer_1_limit - stratosphere_layer_4_limit)
P71 = P51 * (T71 / T51) ** (-G0 / (R_air * L51_71))
L71_84 = -0.002
T84 = T71 + L71_84 * (mesosphere_layer_2_limit - mesosphere_layer_1_limit)
P84 = P71 * (T84 / T71) ** (-G0 / (R_air * L71_84))

# U.S. Standard Atmosphere 1976
# geometric altitude (m), temperature (K), pressure (Pa), density (kg/m^3)

upper_atmosphere_data = [
    (86000.0, 186.8673, 3.7338e-1, 6.9579e-6),
    (90000.0, 186.8673, 1.8359e-1, 3.4160e-6),
    (100000.0, 195.0813, 3.2011e-2, 5.6040e-7),
    (110000.0, 240.0000, 7.1042e-3, 9.7080e-8),
    (120000.0, 360.0000, 2.5382e-3, 2.2220e-8),
    (130000.0, 469.2680, 1.2505e-3, 8.1520e-9),
    (140000.0, 559.6270, 7.2028e-4, 3.8310e-9),
    (150000.0, 634.3920, 4.5422e-4, 2.0760e-9),
    (160000.0, 696.2900, 3.0395e-4, 1.2330e-9),
    (180000.0, 790.0700, 1.5271e-4, 5.1940e-10),
    (200000.0, 854.5600, 8.4736e-5, 2.5410e-10),
    (250000.0, 941.3300, 2.4767e-5, 6.0730e-11),
    (300000.0, 976.0100, 8.7704e-6, 1.9160e-11),
    (400000.0, 995.8300, 1.4518e-6, 2.8030e-12),
    (500000.0, 999.2400, 3.0236e-7, 5.2150e-13),
    (600000.0, 999.8500, 8.2130e-8, 1.1370e-13),
    (700000.0, 999.9700, 3.1908e-8, 3.6140e-14),
    (800000.0, 999.9900, 1.7036e-8, 1.1360e-14),
    (900000.0, 1000.0000, 1.0873e-8, 5.7590e-15),
    (1000000.0, 1000.0000, 7.5138e-9, 3.5610e-15)
]


def upper_atmosphere_interpolate(altitude, value_index):
    if altitude < upper_atmosphere_data[0][0]:
        return upper_atmosphere_data[0][value_index]

    for i in range(len(upper_atmosphere_data) - 1):
        h1 = upper_atmosphere_data[i][0]
        h2 = upper_atmosphere_data[i + 1][0]

        if altitude <= h2:
            value1 = upper_atmosphere_data[i][value_index]
            value2 = upper_atmosphere_data[i + 1][value_index]

            fraction = (altitude - h1) / (h2 - h1)

            if value_index == 1:
                return value1 + fraction * (value2 - value1)

            return math.exp(
                math.log(value1)
                + fraction * (math.log(value2) - math.log(value1))
            )

    raise ValueError("Atmosphere model only valid through 1000 km.")


# simulation settings
dt = 0.01


def acceleration(thrust, mass, current_drag, gravity):
    net_force = thrust + current_drag - mass * gravity

    acceleration = net_force / mass

    return acceleration


def update_mass(mass, mdot, dt):
    new_mass = mass - mdot * dt

    return new_mass


def update_velocity(velocity, acceleration, dt):
    new_velocity = velocity + acceleration * dt

    return new_velocity


def update_altitude(altitude, velocity, dt):
    new_altitude = altitude + velocity * dt

    return new_altitude


def update_time(time, dt):
    new_time = time + dt

    return new_time


def geopotential_altitude(altitude):
    geopotential_altitude = (earth_radius * altitude) / (earth_radius + altitude)

    return geopotential_altitude


def gravitational_acceleration(altitude):
    gravity = G0 * (earth_radius / (earth_radius + altitude)) ** 2

    return gravity


def atmospheric_pressure(altitude):
    H = geopotential_altitude(altitude)

    if H <= troposphere_limit:
        pressure = P0 * (1 - (L * H) / T0) ** (G0 / (R_air * L))
    elif H <= stratosphere_layer_1_limit:
        pressure = P11 * math.exp(-G0 * (H - troposphere_limit) / (R_air * T11))
    elif H <= stratosphere_layer_2_limit:
        temperature = T20 + L20_32 * (H - stratosphere_layer_1_limit)
        pressure = P20 * (temperature / T20) ** (-G0 / (R_air * L20_32))
    elif H <= stratosphere_layer_3_limit:
        temperature = T32 + L32_47 * (H - stratosphere_layer_2_limit)
        pressure = P32 * (temperature / T32) ** (-G0 / (R_air * L32_47))
    elif H <= stratosphere_layer_4_limit:
        pressure = P47 * math.exp(-G0 * (H - stratosphere_layer_3_limit) / (R_air * T47))
    elif H <= mesosphere_layer_1_limit:
        temperature = T51 + L51_71 * (H - stratosphere_layer_4_limit)
        pressure = P51 * (temperature / T51) ** (-G0 / (R_air * L51_71))
    elif H <= mesosphere_layer_2_limit:
        temperature = T71 + L71_84 * (H - mesosphere_layer_1_limit)
        pressure = P71 * (temperature / T71) ** (-G0 / (R_air * L71_84))
    else:
        pressure = upper_atmosphere_interpolate(altitude, 2)

    return pressure


def atmospheric_temperature(altitude):
    H = geopotential_altitude(altitude)

    if H <= troposphere_limit:
        temperature = T0 - L * H
    elif H <= stratosphere_layer_1_limit:
        temperature = T11
    elif H <= stratosphere_layer_2_limit:
        temperature = T20 + L20_32 * (H - stratosphere_layer_1_limit)
    elif H <= stratosphere_layer_3_limit:
        temperature = T32 + L32_47 * (H - stratosphere_layer_2_limit)
    elif H <= stratosphere_layer_4_limit:
        temperature = T47
    elif H <= mesosphere_layer_1_limit:
        temperature = T51 + L51_71 * (H - stratosphere_layer_4_limit)
    elif H <= mesosphere_layer_2_limit:
        temperature = T71 + L71_84 * (H - mesosphere_layer_1_limit)
    else:
        temperature = upper_atmosphere_interpolate(altitude, 1)

    return temperature


def atmospheric_density(altitude):
    H = geopotential_altitude(altitude)

    if H <= mesosphere_layer_2_limit:
        pressure = atmospheric_pressure(altitude)
        temperature = atmospheric_temperature(altitude)

        density = pressure / (R_air * temperature)
    else:
        density = upper_atmosphere_interpolate(altitude, 3)

    return density


def speed_of_sound(temperature):
    sound_speed = math.sqrt(gamma_air * R_air * temperature)

    return sound_speed


def mach_number(velocity, sound_speed):
    mach = abs(velocity) / sound_speed

    return mach


def drag_coefficient(mach):
    if mach <= mach_cd_data[0][0]:
        return mach_cd_data[0][1]

    for i in range(len(mach_cd_data) - 1):
        mach_1, cd_1 = mach_cd_data[i]
        mach_2, cd_2 = mach_cd_data[i + 1]

        if mach <= mach_2:
            cd = cd_1 + ((mach - mach_1) / (mach_2 - mach_1)) * (cd_2 - cd_1)

            return cd

    return mach_cd_data[-1][1]


def drag_force(density, velocity, drag_coefficient, reference_area):
    drag = -0.5 * density * velocity * abs(velocity) * drag_coefficient * reference_area

    return drag


def dynamic_pressure(density, velocity):
    q = 0.5 * density * velocity ** 2

    return q


def flight_environment(altitude, velocity, reference_area):
    pressure = atmospheric_pressure(altitude)
    density = atmospheric_density(altitude)
    gravity = gravitational_acceleration(altitude)
    temperature = atmospheric_temperature(altitude)

    sound_speed = speed_of_sound(temperature)
    mach = mach_number(velocity, sound_speed)
    cd = drag_coefficient(mach)

    drag = drag_force(
        density,
        velocity,
        cd,
        reference_area
    )

    q = dynamic_pressure(density, velocity)

    return pressure, density, gravity, mach, drag, q


def motor_thrust(stage, burn_elapsed, ambient_pressure, engine_data=None):
    if stage.thrust_curve is None:
        mdot, exit_mach, exit_pressure, exit_velocity, exit_area = engine_data
        return nozzle.thrust(
            mdot, exit_velocity, exit_pressure,
            ambient_pressure, exit_area
        )

    curve = stage.thrust_curve

    if burn_elapsed >= curve[-1][0]:
        return 0.0

    for i in range(len(curve) - 1):
        t1, f1 = curve[i]
        t2, f2 = curve[i + 1]

        if burn_elapsed <= t2:
            fraction = (burn_elapsed - t1) / (t2 - t1)
            return f1 + fraction * (f2 - f1)

    return 0.0


def initialize_engine(stage):
    nozzle.validate_inputs(
        stage.Pc,
        stage.Tc,
        stage.gamma,
        stage.R,
        stage.Dt,
        stage.area_ratio,
        P0
    )

    throat_area = math.pi * stage.Dt ** 2 / 4
    exit_area = stage.area_ratio * throat_area

    exit_mach = nozzle.find_exit_mach(
        stage.area_ratio,
        stage.gamma
    )

    exit_temperature, exit_pressure, exit_sound_speed, exit_velocity = nozzle.exit_conditions(
        exit_mach,
        stage.Pc,
        stage.Tc,
        stage.gamma,
        stage.R
    )

    mdot = nozzle.mass_flow_rate(
        stage.Pc,
        stage.Tc,
        stage.gamma,
        stage.R,
        throat_area
    )

    return mdot, exit_mach, exit_pressure, exit_velocity, exit_area


def total_motor_impulse(thrust_curve):
    impulse = 0.0

    for i in range(len(thrust_curve) - 1):
        t1, f1 = thrust_curve[i]
        t2, f2 = thrust_curve[i + 1]

        impulse += 0.5 * (f1 + f2) * (t2 - t1)

    return impulse


def thrust_curve_impulse_between(curve, start_time, end_time):
    impulse = 0.0

    for i in range(len(curve) - 1):
        t1, f1 = curve[i]
        t2, f2 = curve[i + 1]

        a = max(start_time, t1)
        b = min(end_time, t2)

        if b <= a:
            continue

        fa = f1 + (f2 - f1) * (a - t1) / (t2 - t1)
        fb = f1 + (f2 - f1) * (b - t1) / (t2 - t1)

        impulse += 0.5 * (fa + fb) * (b - a)

    return impulse


def simulate_flight(stages, payload_mass=0.0):
    if not stages or payload_mass < 0:
        raise ValueError("Supply at least one stage and a nonnegative payload mass.")
    for stage in stages:
        if stage.dry_mass < 0 or stage.propellant_mass <= 0 or stage.diameter <= 0:
            raise ValueError("Invalid stage mass or diameter.")
        if stage.thrust_curve is None and (stage.Pc is None or stage.Tc is None):
            raise ValueError("Nozzle-driven stages need engine inputs.")
    initial_mass = payload_mass

    for stage in stages:
        initial_mass += stage.dry_mass + stage.propellant_mass

    active_stage = stages[0]
    reference_area = math.pi * active_stage.diameter ** 2 / 4

    time = 0.0
    altitude = 0.0
    velocity = 0.0
    mass = initial_mass

    # flight data
    times = []
    altitudes = []
    velocities = []
    masses = []
    accelerations = []
    drag_forces = []
    densities = []
    mach_numbers = []
    dynamic_pressures = []
    thrust_values = []
    stage_burnout_data = []

    for stage_index, active_stage in enumerate(stages):
        reference_area = math.pi * active_stage.diameter ** 2 / 4

        if active_stage.thrust_curve is None:
            engine_data = initialize_engine(active_stage)
            mdot = engine_data[0]
            burn_duration = active_stage.propellant_mass / mdot
            total_impulse = None
        else:
            engine_data = None
            burn_duration = active_stage.burn_time

            if burn_duration is None or burn_duration <= 0:
                raise ValueError("Thrust-curve stages require a positive burn_time.")

            total_impulse = thrust_curve_impulse_between(
                active_stage.thrust_curve, 0.0, burn_duration
            )

            if total_impulse <= 0:
                raise ValueError("Motor total impulse must be positive.")

        stage_start_time = time
        stage_burnout_mass = mass - active_stage.propellant_mass

        while time - stage_start_time < burn_duration - 1e-10:
            burn_elapsed = time - stage_start_time
            step_dt = min(dt, burn_duration - burn_elapsed)

            current_pressure, current_density, current_gravity, current_mach, current_drag, current_dynamic_pressure = flight_environment(
                altitude,
                velocity,
                reference_area
            )

            current_thrust = motor_thrust(
                active_stage,
                burn_elapsed,
                current_pressure,
                engine_data
            )

            if active_stage.thrust_curve is None:
                propellant_used = mdot * step_dt
            else:
                step_impulse = thrust_curve_impulse_between(
                    active_stage.thrust_curve,
                    burn_elapsed,
                    burn_elapsed + step_dt
                )

                propellant_used = (
                        active_stage.propellant_mass
                        * step_impulse / total_impulse
                )

            # Use the mean thrust over each step, integrating linear curve
            # segments exactly even at a discontinuous transition.
            if active_stage.thrust_curve is not None:
                current_thrust = step_impulse / step_dt

            current_acceleration = acceleration(
                current_thrust,
                mass,
                current_drag,
                current_gravity
            )

            if altitude == 0.0 and velocity == 0.0 and current_acceleration < 0.0:
                current_acceleration = 0.0

            times.append(time)
            altitudes.append(altitude)
            velocities.append(velocity)
            masses.append(mass)
            accelerations.append(current_acceleration)
            drag_forces.append(current_drag)
            densities.append(current_density)
            mach_numbers.append(current_mach)
            dynamic_pressures.append(current_dynamic_pressure)
            thrust_values.append(current_thrust)

            velocity = update_velocity(
                velocity, current_acceleration, step_dt
            )
            altitude = update_altitude(
                altitude, velocity, step_dt
            )

            mass -= propellant_used
            time = update_time(time, step_dt)

        # Verify the integrated propellant use instead of hiding an error.
        if abs(mass - stage_burnout_mass) > 1e-6:
            raise RuntimeError("Propellant mass was not conserved.")

        burnout_data = {
            "stage": stage_index + 1,
            "time": time,
            "altitude": altitude,
            "velocity": velocity,
            "mass": mass,
            "thrust": (0.0 if active_stage.thrust_curve is not None else
                       motor_thrust(active_stage, burn_duration,
                                    atmospheric_pressure(altitude), engine_data)),
            "burn_duration": time - stage_start_time,
        }

        stage_burnout_data.append(burnout_data)

        if stage_index < len(stages) - 1:
            mass -= active_stage.dry_mass

    reference_area = math.pi * stages[-1].diameter ** 2 / 4

    print("\n--- Stage Burnouts ---")

    for burnout in stage_burnout_data:
        print("\nStage", burnout["stage"])
        print("Burnout Time Since Launch:", burnout["time"], "s")
        print("Stage Burn Duration:", burnout["burn_duration"], "s")
        print("Burnout Mass:", burnout["mass"], "kg")
        print("Burnout Altitude:", burnout["altitude"], "m")
        print("Burnout Velocity:", burnout["velocity"], "m/s")
        print("Thrust at Burnout:", burnout["thrust"], "N")

    # coast to apogee
    while velocity > 0 and altitude < 1000000.0:
        current_pressure, current_density, current_gravity, current_mach, current_drag, current_dynamic_pressure = flight_environment(
            altitude,
            velocity,
            reference_area
        )

        current_acceleration = acceleration(
            0.0,
            mass,
            current_drag,
            current_gravity
        )

        if current_acceleration >= 0:
            raise RuntimeError("Coast acceleration must be negative during ascent.")
        step_dt = min(dt, -velocity / current_acceleration)

        times.append(time)
        altitudes.append(altitude)
        velocities.append(velocity)
        masses.append(mass)
        accelerations.append(current_acceleration)
        drag_forces.append(current_drag)
        densities.append(current_density)
        mach_numbers.append(current_mach)
        dynamic_pressures.append(current_dynamic_pressure)
        thrust_values.append(0.0)

        velocity = update_velocity(velocity, current_acceleration, step_dt)
        altitude = update_altitude(altitude, velocity, step_dt)
        time = update_time(time, step_dt)

    # maximum dynamic pressure
    max_q = max(dynamic_pressures)
    max_q_index = dynamic_pressures.index(max_q)
    max_q_time = times[max_q_index]
    max_q_altitude = altitudes[max_q_index]
    max_q_velocity = velocities[max_q_index]
    max_q_mach = mach_numbers[max_q_index]

    # drag sanity check
    max_drag = max(drag_forces, key=abs)
    max_drag_index = drag_forces.index(max_drag)

    print("\n--- Max-Q ---")
    print("Maximum Dynamic Pressure:", max_q, "Pa")
    print("Max-Q Time:", max_q_time, "s")
    print("Max-Q Altitude:", max_q_altitude, "m")
    print("Velocity at Max-Q:", max_q_velocity, "m/s")
    print("Mach at Max-Q:", max_q_mach)

    max_drag_time = times[max_drag_index]
    max_drag_altitude = altitudes[max_drag_index]
    max_drag_velocity = velocities[max_drag_index]

    print("\n--- Drag Validation ---")
    print("Initial Drag:", abs(drag_forces[0]), "N")
    print("Maximum Drag:", abs(max_drag), "N")
    print("Maximum Drag Time:", max_drag_time, "s")
    print("Maximum Drag Altitude:", max_drag_altitude, "m")
    print("Velocity at Maximum Drag:", max_drag_velocity, "m/s")

    if altitude >= 1000000.0:
        print("\nWARNING: Simulation exceeded 1000 km.")
        print("Apogee was not reached within the atmosphere model.")

    print("\n--- Coast ---")
    print("Apogee Time:", time, "s")
    print("Apogee Altitude:", altitude, "m")
    print("Velocity at End:", velocity, "m/s")

    return {
        "initial_mass_kg": initial_mass,
        "apogee_m": altitude,
        "apogee_time_s": time,
        "max_q_pa": max_q,
        "max_drag_n": abs(max_drag),
        "burnouts": stage_burnout_data,
        "final_mass_kg": mass,
        "time_s": times,
        "altitude_m": altitudes,
        "velocity_m_s": velocities,
        "mass_kg": masses,
        "acceleration_m_s2": accelerations,
        "drag_n": drag_forces,
        "density_kg_m3": densities,
        "mach": mach_numbers,
        "dynamic_pressure_pa": dynamic_pressures,
        "thrust_n": thrust_values,
    }



def plot_flight(results):
    import matplotlib.pyplot as plt

    # get the values saved during the simulation
    time = results["time_s"]
    altitude = [height / 1000 for height in results["altitude_m"]]
    velocity = results["velocity_m_s"]
    acceleration = results["acceleration_m_s2"]
    pressure = [q / 1000 for q in results["dynamic_pressure_pa"]]
    thrust = [force / 1000 for force in results["thrust_n"]]
    mass = results["mass_kg"]

    # use four rows so titles and labels have enough room
    fig, graphs = plt.subplots(4, 2, figsize=(15, 13), layout="constrained")
    fig.suptitle("Multistage Rocket Flight Simulation", fontsize=15)

    graphs[0, 0].plot(time, altitude)
    graphs[0, 0].set_title("Altitude")
    graphs[0, 0].set_ylabel("Altitude (km)")

    graphs[0, 1].plot(time, velocity)
    graphs[0, 1].set_title("Velocity")
    graphs[0, 1].set_ylabel("Velocity (m/s)")

    graphs[1, 0].plot(time, acceleration)
    graphs[1, 0].set_title("Vertical Acceleration")
    graphs[1, 0].set_ylabel("Acceleration (m/s^2)")

    graphs[1, 1].plot(time, pressure)
    graphs[1, 1].set_title("Dynamic Pressure")
    graphs[1, 1].set_ylabel("Dynamic Pressure (kPa)")

    graphs[2, 0].plot(time, thrust)
    graphs[2, 0].set_title("Thrust")
    graphs[2, 0].set_ylabel("Thrust (kN)")

    graphs[2, 1].plot(time, mass)
    graphs[2, 1].set_title("Vehicle Mass")
    graphs[2, 1].set_ylabel("Mass (kg)")

    # zoom in on the powered part of the flight
    graphs[3, 0].plot(time, velocity)
    graphs[3, 0].set_title("Velocity: First 35 Seconds")
    graphs[3, 0].set_ylabel("Velocity (m/s)")
    graphs[3, 0].set_xlim(0, 35)

    graphs[3, 1].plot(time, pressure)
    graphs[3, 1].set_title("Dynamic Pressure: First 35 Seconds")
    graphs[3, 1].set_ylabel("Dynamic Pressure (kPa)")
    graphs[3, 1].set_xlim(0, 35)

    for burnout in results["burnouts"]:
        for graph in graphs.flat:
            graph.axvline(burnout["time"], color="gray", linestyle="--")

    max_q = max(pressure)
    max_q_index = pressure.index(max_q)
    graphs[1, 1].plot(time[max_q_index], max_q, "ro")
    graphs[0, 0].plot(results["apogee_time_s"], results["apogee_m"] / 1000, "ro")
    graphs[0, 1].plot(results["apogee_time_s"], 0, "ro")

    for graph in graphs.flat:
        graph.set_xlabel("Time (s)")
        graph.grid(True)
        graph.tick_params(labelsize=9)
        graph.title.set_fontsize(11)

    plt.show()


if __name__ == "__main__":
    print("Simulated Launch Mass:", simulated_initial_mass, "kg")
    print("Published Approximate Vehicle Mass:", reference_vehicle_mass, "kg")
    print("Published Reference + Assumed Payload:", reference_initial_mass, "kg")
    print("Mass Difference (not independent validation):", mass_difference, "kg")
    print("\n--- Motor Impulse Analysis ---")

    for i, stage in enumerate(stages, start=1):
        impulse = total_motor_impulse(stage.thrust_curve)

        print(f"Stage {i} Total Impulse: {impulse:.1f} N*s")

        for isp in (200.0, 230.0, 260.0):
            propellant_mass = impulse / (G0 * isp)

            print(
                f"  At Isp = {isp:.0f} s: "
                f"propellant mass = {propellant_mass:.2f} kg"
            )
    results = simulate_flight(stages, payload_mass)
    plot_flight(results)
