import os
import subprocess
import numpy as np
import logging
from datetime import datetime

class TrajectoryTrackerGains:
    def __init__(self, kp_cross_track, kd_cross_track, kp_vel_cross_track, kd_vel_cross_track,
                 kp_along_track, kd_along_track, kp_vel_along_track, kd_vel_along_track,
                 kp_z_track, kd_z_track, kp_vel_z, kd_vel_z,
                 kp_yaw, kd_yaw):
        self.kp_cross_track = kp_cross_track
        self.kd_cross_track = kd_cross_track
        self.kp_vel_cross_track = kp_vel_cross_track
        self.kd_vel_cross_track = kd_vel_cross_track
        self.kp_along_track = kp_along_track
        self.kd_along_track = kd_along_track
        self.kp_vel_along_track = kp_vel_along_track
        self.kd_vel_along_track = kd_vel_along_track
        self.kp_z_track = kp_z_track
        self.kd_z_track = kd_z_track
        self.kp_vel_z = kp_vel_z
        self.kd_vel_z = kd_vel_z
        self.kp_yaw = kp_yaw
        self.kd_yaw = kd_yaw

    def __repr__(self):
        return (f"kp_cross_track: {self.kp_cross_track}, kd_cross_track: {self.kd_cross_track}, "
                f"kp_vel_cross_track: {self.kp_vel_cross_track}, kd_vel_cross_track: {self.kd_vel_cross_track}, "
                f"kp_along_track: {self.kp_along_track}, kd_along_track: {self.kd_along_track}, "
                f"kp_vel_along_track: {self.kp_vel_along_track}, kd_vel_along_track: {self.kd_vel_along_track}, "
                f"kp_z_track: {self.kp_z_track}, kd_z_track: {self.kd_z_track}, "
                f"kp_vel_z: {self.kp_vel_z}, kd_vel_z: {self.kd_vel_z}, "
                f"kp_yaw: {self.kp_yaw}, kd_yaw: {self.kd_yaw}")

def evaluate_params(gains, vel_max, acc_max, generation, individual_idx, n_tests=30):
    total_time = 0
    times = []
    outputs = []
    # Create directories for storing results
    gen_dir = f"Generation_{generation}"
    indiv_dir = os.path.join(gen_dir, f"Individual_{individual_idx}")
    os.makedirs(indiv_dir, exist_ok=True)
    # Create parameters file
    params_file = os.path.join(indiv_dir, f"test_conditions_g{generation}t{individual_idx}.txt")
    with open(params_file, 'w') as f:
        f.write(f"kp_cross_track={gains.kp_cross_track},\n")
        f.write(f"kd_cross_track={gains.kd_cross_track},\n")
        f.write(f"kp_vel_cross_track={gains.kp_vel_cross_track},\n")
        f.write(f"kd_vel_cross_track={gains.kd_vel_cross_track},\n")
        f.write(f"kp_along_track={gains.kp_along_track},\n")
        f.write(f"kd_along_track={gains.kd_along_track},\n")
        f.write(f"kp_vel_along_track={gains.kp_vel_along_track},\n")
        f.write(f"kd_vel_along_track={gains.kd_vel_along_track},\n")
        f.write(f"kp_z_track={gains.kp_z_track},\n")
        f.write(f"kd_z_track={gains.kd_z_track},\n")
        f.write(f"kp_vel_z={gains.kp_vel_z},\n")
        f.write(f"kd_vel_z={gains.kd_vel_z},\n")
        f.write(f"kp_yaw={gains.kp_yaw},\n")
        f.write(f"kd_yaw={gains.kd_yaw},\n")
        f.write(f"vel_max={vel_max},\n")
        f.write(f"acc_max={acc_max},\n")
    # Run n_tests times
    for test_idx in range(1, n_tests+1):
        # Call the PowerShell script
        script = "RunAirSim.ps1"
        params_filename = os.path.abspath(params_file)
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script, "-f", params_filename]
        # Start timing
        start_time = datetime.now()
        try:
            # Run the script and capture output
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, text=True)
            end_time = datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            # Parse the time from the output if available
            output = result.stdout
            outputs.append(output)
            # Extract time from output
            lap_time = None
            for line in output.splitlines():
                if "Time In Between (in nanoseconds):" in line:
                    nanoseconds = int(line.split(":")[1].strip())
                    lap_time = nanoseconds / 1e9  # Convert to seconds
                    break
            if lap_time is None:
                lap_time = 1000  # Punish if time not found
            times.append(lap_time)
            total_time += lap_time
        except subprocess.TimeoutExpired:
            # If the process times out, punish with time 1000
            outputs.append("Process timed out")
            times.append(1000)
            total_time += 1000
        except Exception as e:
            outputs.append(f"Process failed: {e}")
            times.append(1000)
            total_time += 1000
        # Save individual result
        result_file = os.path.join(indiv_dir, f"result_{test_idx}.txt")
        with open(result_file, 'w') as f:
            f.write(f"Test {test_idx} Output:\n{outputs[-1]}\n")
            f.write(f"Lap Time: {times[-1]} seconds\n")
    # Calculate average time
    average_time = total_time / n_tests
    # Write results to "results_g{generation}t{individual_idx}.txt"
    results_file = os.path.join(indiv_dir, f"results_g{generation}t{individual_idx}.txt")
    with open(results_file, 'w') as f:
        f.write(f"Average Lap Time: {average_time:.2f} seconds\n")
        f.write("Individual Test Results:\n")
        for idx, (time_i, output_i) in enumerate(zip(times, outputs), start=1):
            f.write(f"Test {idx}: Lap Time: {time_i:.2f} seconds\n")
            f.write(f"Output:\n{output_i}\n\n")
    return average_time

def mutate_params(gains, mutation_rate=0.1):
    mutated_gains = gains.__dict__.copy()
    for key in mutated_gains:
        if np.random.rand() < mutation_rate:
            mutated_gains[key] += np.random.normal(0, 1)  # Adjust standard deviation as needed
    return TrajectoryTrackerGains(**mutated_gains)

def setup_logging():
    logging.basicConfig(filename='genetic_algorithm_log.txt',
                        filemode='w',  # Use 'a' to append to the file
                        format='%(asctime)s - %(message)s',
                        level=logging.INFO)

def genetic_algorithm(n_generations=50, population_size=20):
    setup_logging()
    # Initial population
    population = [TrajectoryTrackerGains(7.0, 7.0, 3.0, 3.0, 0.9, 0.9, 0.09, 0.09, 3.0, 3.0, 0.9, 0.9, 9.0, 9.0) for _ in range(population_size)]
    vel_max, acc_max = 80.0, 80.0

    for generation in range(1, n_generations+1):
        print(f"Generation {generation}/{n_generations}")
        fitness_scores = []
        for idx, gains in enumerate(population, start=1):
            average_time = evaluate_params(gains, vel_max, acc_max, generation, idx, n_tests=30)
            fitness_scores.append(average_time)

        # Find the best individual for this generation
        best_idx = np.argmin(fitness_scores)
        best_gains = population[best_idx]
        best_lap_time = fitness_scores[best_idx]

        logging.info(f"Generation {generation}: Best lap time: {best_lap_time:.2f} seconds "
                     f"with gains: {best_gains}")

        # Log the lap time for each individual
        for i, (gains, lap_time) in enumerate(zip(population, fitness_scores)):
            logging.info(f"Generation {generation}, Individual {i+1}: Lap time: {lap_time:.2f} seconds, Gains: {gains}")

        # Create new population from the best individual
        new_population = []
        for _ in range(population_size):
            child = mutate_params(best_gains)
            new_population.append(child)
            logging.info(f"Generation {generation}: Parent gains: {best_gains}, Child gains: {child}")

        population = new_population

if __name__ == "__main__":
    genetic_algorithm()

    # python genetic_algorithm.py