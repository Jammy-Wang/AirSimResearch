# import airsimneurips
# import numpy as np
# import math
# import sys
# import time
# from airsimneurips import Vector3r, TrajectoryTrackerGains
# from datetime import datetime

# # Read the parameters file from command-line arguments
# if len(sys.argv) < 2:
#     print("Usage: python flighttest.py <parameters_file>")
#     sys.exit(1)

# parameters_file = sys.argv[1]

# # Function to read parameters from the text file
# def read_parameters(file_path):
#     params = {}
#     with open(file_path, 'r') as f:
#         for line in f:
#             line = line.strip().rstrip(',')
#             if line:
#                 key_value = line.split('=')
#                 if len(key_value) == 2:
#                     key = key_value[0].strip()
#                     value = float(key_value[1].strip())
#                     params[key] = value
#     return params

# # Read parameters
# params = read_parameters(parameters_file)

# # Extract parameters with default values if not provided
# kp_cross_track = params.get('kp_cross_track', 0)
# kd_cross_track = params.get('kd_cross_track', 0)
# kp_vel_cross_track = params.get('kp_vel_cross_track', 0)
# kd_vel_cross_track = params.get('kd_vel_cross_track', 0)
# kp_along_track = params.get('kp_along_track', 0)
# kd_along_track = params.get('kd_along_track', 0)
# kp_vel_along_track = params.get('kp_vel_along_track', 0)
# kd_vel_along_track = params.get('kd_vel_along_track', 0)
# kp_z_track = params.get('kp_z_track', 0)
# kd_z_track = params.get('kd_z_track', 0)
# kp_vel_z = params.get('kp_vel_z', 0)
# kd_vel_z = params.get('kd_vel_z', 0)
# kp_yaw = params.get('kp_yaw', 0)
# kd_yaw = params.get('kd_yaw', 0)
# vel_max = params.get('vel_max', 0)
# acc_max = params.get('acc_max', 0)

# # Connect to server with drone controls
# client = airsimneurips.MultirotorClient()
# client.confirmConnection()
# print('Connection confirmed')

# # Load level and initialize the drone
# client.simLoadLevel('Qualifier_Tier_3')
# client.enableApiControl(vehicle_name="drone_1")
# client.arm(vehicle_name="drone_1")
# client.simStartRace()

# drone_name = "drone_1"
# viz_traj = False
# viz_traj_color_rgba = [1.0, 0.0, 0.0, 1.0]
# takeoff_height = 1
# MAX_NUMBER_OF_GETOBJECTPOSE_TRIALS = 10

# traj_tracker_gains = TrajectoryTrackerGains(
#     kp_cross_track=kp_cross_track, kd_cross_track=kd_cross_track,
#     kp_vel_cross_track=kp_vel_cross_track, kd_vel_cross_track=kd_vel_cross_track,
#     kp_along_track=kp_along_track, kd_along_track=kd_along_track,
#     kp_vel_along_track=kp_vel_along_track, kd_vel_along_track=kd_vel_along_track,
#     kp_z_track=kp_z_track, kd_z_track=kd_z_track,
#     kp_vel_z=kp_vel_z, kd_vel_z=kd_vel_z,
#     kp_yaw=kp_yaw, kd_yaw=kd_yaw
# )

# client.setTrajectoryTrackerGains(traj_tracker_gains, vehicle_name=drone_name)
# time.sleep(0.2)

# # Takeoff
# start_position = client.simGetVehiclePose(vehicle_name=drone_name).position
# takeoff_waypoint = Vector3r(start_position.x_val, start_position.y_val, start_position.z_val - takeoff_height)

# client.moveOnSplineAsync(
#     [takeoff_waypoint],
#     vel_max=15.0, acc_max=5.0,
#     add_position_constraint=True, add_velocity_constraint=False, add_acceleration_constraint=False,
#     viz_traj=viz_traj, viz_traj_color_rgba=viz_traj_color_rgba,
#     vehicle_name=drone_name
# ).join()

# # Get gate poses
# gate_names_sorted_bad = sorted(client.simListSceneObjects("Gate.*"))
# gate_indices_bad = [int(gate_name.split('_')[0][4:]) for gate_name in gate_names_sorted_bad]
# gate_indices_correct = sorted(range(len(gate_indices_bad)), key=lambda k: gate_indices_bad[k])
# gate_names_sorted = [gate_names_sorted_bad[gate_idx] for gate_idx in gate_indices_correct]

# gate_poses_ground_truth = []
# for gate_name in gate_names_sorted:
#     curr_pose = client.simGetObjectPose(gate_name)
#     counter = 0
#     while (math.isnan(curr_pose.position.x_val) or math.isnan(curr_pose.position.y_val) or math.isnan(curr_pose.position.z_val)) and (counter < MAX_NUMBER_OF_GETOBJECTPOSE_TRIALS):
#         print(f"DEBUG: {gate_name} position is nan, retrying...")
#         counter += 1
#         curr_pose = client.simGetObjectPose(gate_name)
#     assert not math.isnan(curr_pose.position.x_val), f"ERROR: {gate_name} curr_pose.position.x_val is still {curr_pose.position.x_val} after {counter} trials"
#     assert not math.isnan(curr_pose.position.y_val), f"ERROR: {gate_name} curr_pose.position.y_val is still {curr_pose.position.y_val} after {counter} trials"
#     assert not math.isnan(curr_pose.position.z_val), f"ERROR: {gate_name} curr_pose.position.z_val is still {curr_pose.position.z_val} after {counter} trials"
#     gate_poses_ground_truth.append(curr_pose)

# # Variables to store the timestamps
# start_time = None
# finish_time = None

# # Variables to store positions and speeds during the flight between first and last gates
# positions = []
# speeds = []
# max_speed = 0.0

# # Start the drone's movement
# spline_flight = client.moveOnSplineAsync(
#     [gate_pose.position for gate_pose in gate_poses_ground_truth],
#     vel_max=vel_max, acc_max=acc_max,
#     add_position_constraint=False, add_velocity_constraint=False, add_acceleration_constraint=False,
#     viz_traj=viz_traj, viz_traj_color_rgba=viz_traj_color_rgba,
#     vehicle_name=drone_name
# )

# # Monitor the drone's position in the main thread
# first_gate_crossed = False
# last_gate_crossed = False

# # Get first and last gate positions
# first_gate_pose = gate_poses_ground_truth[0]
# first_gate_position = np.array([
#     first_gate_pose.position.x_val,
#     first_gate_pose.position.y_val,
#     first_gate_pose.position.z_val
# ])

# last_gate_pose = gate_poses_ground_truth[-1]
# last_gate_position = np.array([
#     last_gate_pose.position.x_val,
#     last_gate_pose.position.y_val,
#     last_gate_pose.position.z_val
# ])

# # Function to compute distance between two points
# def distance(p1, p2):
#     return np.linalg.norm(p1 - p2)

# # Set a maximum monitoring time to prevent infinite loops
# max_monitoring_time = 120  # seconds
# monitoring_start_time = time.time()

# while not last_gate_crossed:
#     # Get drone position
#     drone_pose = client.simGetVehiclePose(vehicle_name=drone_name)
#     drone_position = np.array([
#         drone_pose.position.x_val,
#         drone_pose.position.y_val,
#         drone_pose.position.z_val
#     ])

#     # Check if the drone has passed the first gate
#     if not first_gate_crossed:
#         dist_to_first_gate = distance(drone_position, first_gate_position)
#         if dist_to_first_gate < 2.0:  # Threshold distance (adjust as needed)
#             start_time = datetime.now()
#             print("Passed first gate at time:", start_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
#             first_gate_crossed = True

#     # Check if the drone has passed the last gate
#     if first_gate_crossed and not last_gate_crossed:
#         dist_to_last_gate = distance(drone_position, last_gate_position)
#         if dist_to_last_gate < 2.0:  # Threshold distance (adjust as needed)
#             finish_time = datetime.now()
#             print("Passed last gate at time:", finish_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
#             last_gate_crossed = True

#     # Get drone velocity
#     drone_velocity = client.getMultirotorState(vehicle_name=drone_name).kinematics_estimated.linear_velocity
#     speed = np.linalg.norm([drone_velocity.x_val, drone_velocity.y_val, drone_velocity.z_val])

#     # Record positions and speeds between first and last gate
#     if first_gate_crossed and not last_gate_crossed:
#         positions.append(drone_position)
#         speeds.append(speed)
#         if speed > max_speed:
#             max_speed = speed

#     # Terminate if the drone has stopped moving significantly
#     if speed < 0.5 and first_gate_crossed:
#         print("Drone has stopped moving.")
#         break

#     # Check for maximum monitoring time
#     elapsed_time = time.time() - monitoring_start_time
#     if elapsed_time > max_monitoring_time:
#         print("Maximum monitoring time exceeded.")
#         break

#     time.sleep(0.01)  # Sleep for 10ms to reduce CPU usage

# # Wait for the spline flight to finish
# spline_flight.join()

# # Compute and print the time difference
# if start_time and finish_time:
#     time_difference = finish_time - start_time
#     print("Time between first and last gate:", time_difference)
#     nanoseconds = time_difference.total_seconds() * 1_000_000_000
#     print("Time In Between (in nanoseconds):", int(nanoseconds))

#     # Compute total distance traveled between first and last gates
#     if len(positions) > 1:
#         total_distance = 0.0
#         for i in range(1, len(positions)):
#             dist = np.linalg.norm(positions[i] - positions[i - 1])
#             total_distance += dist
#         time_difference_seconds = time_difference.total_seconds()
#         average_speed = total_distance / time_difference_seconds
#         print("Average speed between first and last gates: {:.2f} m/s".format(average_speed))
#         print("Top speed between first and last gates: {:.2f} m/s".format(max_speed))
#     else:
#         print("Not enough data to compute average speed and top speed.")
# else:
#     print("Failed to measure time between gates.")



import airsimneurips
import numpy as np
import math
import sys
import time
import os
from airsimneurips import Vector3r, TrajectoryTrackerGains
from datetime import datetime

# Read the parameters file from command-line arguments
if len(sys.argv) < 2:
    print("Usage: python flighttest.py <parameters_file>")
    sys.exit(1)

parameters_file = sys.argv[1]

# Extract base filename without extension
base_filename = os.path.splitext(parameters_file)[0].replace("_tc", "")

# Define log and results file names
log_filename = f"{base_filename}_log.txt"
results_filename = f"{base_filename}_results.txt"

# Open log file for writing
log_file = open(log_filename, 'a')

# Function to read parameters from the text file
def read_parameters(file_path):
    params = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip().rstrip(',')
            if line:
                key_value = line.split('=')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = float(key_value[1].strip())
                    params[key] = value
    return params

# Read parameters
params = read_parameters(parameters_file)

# Extract parameters with default values if not provided
kp_cross_track = params.get('kp_cross_track', 0)
kd_cross_track = params.get('kd_cross_track', 0)
kp_vel_cross_track = params.get('kp_vel_cross_track', 0)
kd_vel_cross_track = params.get('kd_vel_cross_track', 0)
kp_along_track = params.get('kp_along_track', 0)
kd_along_track = params.get('kd_along_track', 0)
kp_vel_along_track = params.get('kp_vel_along_track', 0)
kd_vel_along_track = params.get('kd_vel_along_track', 0)
kp_z_track = params.get('kp_z_track', 0)
kd_z_track = params.get('kd_z_track', 0)
kp_vel_z = params.get('kp_vel_z', 0)
kd_vel_z = params.get('kd_vel_z', 0)
kp_yaw = params.get('kp_yaw', 0)
kd_yaw = params.get('kd_yaw', 0)
vel_max = params.get('vel_max', 0)
acc_max = params.get('acc_max', 0)

# Connect to server with drone controls
client = airsimneurips.MultirotorClient()
client.confirmConnection()
log_file.write('Connection confirmed\n')

# Load level and initialize the drone
client.simLoadLevel('Qualifier_Tier_3')
client.enableApiControl(vehicle_name="drone_1")
client.arm(vehicle_name="drone_1")
client.simStartRace()

drone_name = "drone_1"
viz_traj = False
viz_traj_color_rgba = [1.0, 0.0, 0.0, 1.0]
takeoff_height = 1
MAX_NUMBER_OF_GETOBJECTPOSE_TRIALS = 10

traj_tracker_gains = TrajectoryTrackerGains(
    kp_cross_track=kp_cross_track, kd_cross_track=kd_cross_track,
    kp_vel_cross_track=kp_vel_cross_track, kd_vel_cross_track=kd_vel_cross_track,
    kp_along_track=kp_along_track, kd_along_track=kd_along_track,
    kp_vel_along_track=kp_vel_along_track, kd_vel_along_track=kd_vel_along_track,
    kp_z_track=kp_z_track, kd_z_track=kd_z_track,
    kp_vel_z=kp_vel_z, kd_vel_z=kd_vel_z,
    kp_yaw=kp_yaw, kd_yaw=kd_yaw
)

client.setTrajectoryTrackerGains(traj_tracker_gains, vehicle_name=drone_name)
time.sleep(0.2)

# Takeoff
start_position = client.simGetVehiclePose(vehicle_name=drone_name).position
takeoff_waypoint = Vector3r(start_position.x_val, start_position.y_val, start_position.z_val - takeoff_height)

client.moveOnSplineAsync(
    [takeoff_waypoint],
    vel_max=15.0, acc_max=5.0,
    add_position_constraint=True, add_velocity_constraint=False, add_acceleration_constraint=False,
    viz_traj=viz_traj, viz_traj_color_rgba=viz_traj_color_rgba,
    vehicle_name=drone_name
).join()

# Get gate poses
gate_names_sorted_bad = sorted(client.simListSceneObjects("Gate.*"))
gate_indices_bad = [int(gate_name.split('_')[0][4:]) for gate_name in gate_names_sorted_bad]
gate_indices_correct = sorted(range(len(gate_indices_bad)), key=lambda k: gate_indices_bad[k])
gate_names_sorted = [gate_names_sorted_bad[gate_idx] for gate_idx in gate_indices_correct]

gate_poses_ground_truth = []
for gate_name in gate_names_sorted:
    curr_pose = client.simGetObjectPose(gate_name)
    counter = 0
    while (math.isnan(curr_pose.position.x_val) or math.isnan(curr_pose.position.y_val) or math.isnan(curr_pose.position.z_val)) and (counter < MAX_NUMBER_OF_GETOBJECTPOSE_TRIALS):
        log_file.write(f"DEBUG: {gate_name} position is nan, retrying...\n")
        counter += 1
        curr_pose = client.simGetObjectPose(gate_name)
    if math.isnan(curr_pose.position.x_val) or math.isnan(curr_pose.position.y_val) or math.isnan(curr_pose.position.z_val):
        log_file.write(f"ERROR: {gate_name} position has NaN values after {counter} trials\n")
    else:
        gate_poses_ground_truth.append(curr_pose)

# Variables to store the timestamps
start_time = None
finish_time = None

# Variables to store positions and speeds during the flight between first and last gates
positions = []
speeds = []
max_speed = 0.0

# Start the drone's movement
spline_flight = client.moveOnSplineAsync(
    [gate_pose.position for gate_pose in gate_poses_ground_truth],
    vel_max=vel_max, acc_max=acc_max,
    add_position_constraint=False, add_velocity_constraint=False, add_acceleration_constraint=False,
    viz_traj=viz_traj, viz_traj_color_rgba=viz_traj_color_rgba,
    vehicle_name=drone_name
)

# Monitor the drone's position in the main thread
first_gate_crossed = False
last_gate_crossed = False

# Get first and last gate positions
first_gate_pose = gate_poses_ground_truth[0]
first_gate_position = np.array([
    first_gate_pose.position.x_val,
    first_gate_pose.position.y_val,
    first_gate_pose.position.z_val
])

last_gate_pose = gate_poses_ground_truth[-1]
last_gate_position = np.array([
    last_gate_pose.position.x_val,
    last_gate_pose.position.y_val,
    last_gate_pose.position.z_val
])

# Function to compute distance between two points
def distance(p1, p2):
    return np.linalg.norm(p1 - p2)

# Set a maximum monitoring time to prevent infinite loops
max_monitoring_time = 120  # seconds
monitoring_start_time = time.time()

while not last_gate_crossed:
    # Get drone position
    drone_pose = client.simGetVehiclePose(vehicle_name=drone_name)
    drone_position = np.array([
        drone_pose.position.x_val,
        drone_pose.position.y_val,
        drone_pose.position.z_val
    ])

    # Check if the drone has passed the first gate
    if not first_gate_crossed:
        dist_to_first_gate = distance(drone_position, first_gate_position)
        if dist_to_first_gate < 2.0:  # Threshold distance (adjust as needed)
            start_time = datetime.now()
            log_file.write("Passed first gate at time: {}\n".format(start_time.strftime("%Y-%m-%d %H:%M:%S.%f")))
            first_gate_crossed = True

    # Check if the drone has passed the last gate
    if first_gate_crossed and not last_gate_crossed:
        dist_to_last_gate = distance(drone_position, last_gate_position)
        if dist_to_last_gate < 2.0:  # Threshold distance (adjust as needed)
            finish_time = datetime.now()
            log_file.write("Passed last gate at time: {}\n".format(finish_time.strftime("%Y-%m-%d %H:%M:%S.%f")))
            last_gate_crossed = True

    # Get drone velocity
    drone_velocity = client.getMultirotorState(vehicle_name=drone_name).kinematics_estimated.linear_velocity
    speed = np.linalg.norm([drone_velocity.x_val, drone_velocity.y_val, drone_velocity.z_val])

    # Record positions and speeds between first and last gate
    if first_gate_crossed and not last_gate_crossed:
        positions.append(drone_position)
        speeds.append(speed)
        if speed > max_speed:
            max_speed = speed

    # Terminate if the drone has stopped moving significantly
    if speed < 0.5 and first_gate_crossed:
        log_file.write("Drone has stopped moving.\n")
        break

    # Check for maximum monitoring time
    elapsed_time = time.time() - monitoring_start_time
    if elapsed_time > max_monitoring_time:
        log_file.write("Maximum monitoring time exceeded.\n")
        break

    time.sleep(0.01)  # Sleep for 10ms to reduce CPU usage

# Wait for the spline flight to finish
spline_flight.join()

# Compute and write the results
if start_time and finish_time:
    time_difference = finish_time - start_time
    log_file.write("Time between first and last gate: {}\n".format(time_difference))
    nanoseconds = time_difference.total_seconds() * 1_000_000_000
    log_file.write("Time In Between (in nanoseconds): {}\n".format(int(nanoseconds)))

    # Compute total distance traveled between first and last gates
    if len(positions) > 1:
        total_distance = 0.0
        for i in range(1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[i - 1])
            total_distance += dist
        time_difference_seconds = time_difference.total_seconds()
        average_speed = total_distance / time_difference_seconds
        log_file.write("Average speed between first and last gates: {:.2f} m/s\n".format(average_speed))
        log_file.write("Top speed between first and last gates: {:.2f} m/s\n".format(max_speed))
        
        # Write results to the results file
        with open(results_filename, 'a') as results_file:
            results_file.write("Lap time: {}\n".format(time_difference))
            results_file.write("Average speed: {:.2f} m/s\n".format(average_speed))
            results_file.write("Top speed: {:.2f} m/s\n".format(max_speed))
    else:
        log_file.write("Not enough data to compute average speed and top speed.\n")
        with open(results_filename, 'a') as results_file:
            results_file.write("Failed to compute speeds.\n")
else:
    log_file.write("Failed to measure time between gates.\n")
    with open(results_filename, 'a') as results_file:
        results_file.write("Failed to measure lap time.\n")

# Close the log file
log_file.close()
