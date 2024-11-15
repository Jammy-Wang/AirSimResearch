import sys
import re
from datetime import timedelta

def parse_time(time_str):
    """Convert lap time string into a timedelta object."""
    try:
        time_parts = re.findall(r"(\d+):(\d+):([\d.]+)", time_str)
        if time_parts:
            hours, minutes, seconds = map(float, time_parts[0])
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except Exception as e:
        print(f"Error parsing time: {time_str}, {e}")
    return None

def find_best_run(file_path):
    try:
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]  # Remove empty lines
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    # Debug: Print lines read from the file
    print("Debug: Lines read from the results file:")
    for i, line in enumerate(lines):
        print(f"{i}: {line}")

    # Check if the first line indicates a defective PID combination
    if lines and lines[0].strip() == "This PID combination is defective":
        print("This PID combination is defective. Exiting.")
        return

    # Parse runs and extract data
    run_data = []
    current_run = {}

    for line in lines:
        if "Run" in line:
            # Save the previous run if it is complete
            if "lap_time" in current_run:
                run_data.append(current_run)
                print(f"Debug: Added run data: {current_run}")
            # Start a new run
            current_run = {"run_number": line.strip()}
        elif "Lap time:" in line:
            lap_time = parse_time(line.split(":")[1].strip())
            if lap_time:
                current_run["lap_time"] = lap_time
        elif "Average speed:" in line:
            try:
                current_run["avg_speed"] = float(line.split(":")[1].strip().split()[0])
            except Exception as e:
                print(f"Error parsing average speed: {line}, {e}")
        elif "Top speed:" in line:
            try:
                current_run["top_speed"] = float(line.split(":")[1].strip().split()[0])
            except Exception as e:
                print(f"Error parsing top speed: {line}, {e}")

    # Add the last run if it is valid
    if "lap_time" in current_run:
        run_data.append(current_run)
        print(f"Debug: Added run data: {current_run}")

    # Debug: Print parsed run data
    print("Debug: Parsed run data:")
    for run in run_data:
        print(run)

    if not run_data:
        print("No valid runs found in the results file.")
        return

    # Find the best run based on the shortest lap time
    best_run = min(run_data, key=lambda x: x["lap_time"])

    # Calculate averages
    avg_lap_time = sum(run["lap_time"].total_seconds() for run in run_data) / len(run_data)
    avg_speed = sum(run["avg_speed"] for run in run_data) / len(run_data)
    avg_top_speed = sum(run["top_speed"] for run in run_data) / len(run_data)

    avg_lap_time_td = timedelta(seconds=avg_lap_time)

    # Prepend the results file with the best run and averages
    try:
        with open(file_path, "r") as file:
            content = file.read()

        with open(file_path, "w") as file:
            file.write(
                f"Best run: {best_run['run_number']}\n"
                f"Lap time: {best_run['lap_time']}\n"
                f"Average speed: {best_run['avg_speed']:.2f} m/s\n"
                f"Top speed: {best_run['top_speed']:.2f} m/s\n\n"
                f"Overall averages:\n"
                f"Lap time: {avg_lap_time_td}\n"
                f"Average speed: {avg_speed:.2f} m/s\n"
                f"Top speed: {avg_top_speed:.2f} m/s\n\n"
            )
            file.write(content)

        print("Best run and averages prepended to the results file.")

    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python FindBestRun.py <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    find_best_run(results_file)
