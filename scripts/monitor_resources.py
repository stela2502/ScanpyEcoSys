#! /usr/bin/env python3

import psutil
import time
import sys


# Module-level variables to cache NVML state
NVML_INITIALIZED = False
DEVICE_COUNT = 0


try:
    from pynvml import (
        nvmlInit,
        nvmlDeviceGetCount,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetUtilizationRates,
        nvmlShutdown,
    )
    from pynvml.nvml import (
            NVMLError_LibraryNotFound,
            NVMLError_Uninitialized,
    )

    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


# Function to initialize NVML
def initialize_nvml():
    global NVML_INITIALIZED, DEVICE_COUNT
    if not NVML_INITIALIZED:
        try:
            nvmlInit()
            NVML_INITIALIZED = True
            DEVICE_COUNT = nvmlDeviceGetCount()
        except NVMLError_LibraryNotFound:
            print({"Error: NVML Library not found; skipping GPU monitoring."}, file=sys.stderr)
        except NVMLError_Uninitialized:
            print({"Error: NVML Device is uninitialized; skipping GPU monitoring."}, file=sys.stderr)
        except Exception as e:
            NVML_INITIALIZED = False
            print(f"Failed to initialize NVML: {e}", file=sys.stderr)

# Function to shutdown NVML
def shutdown_nvml():
    global NVML_INITIALIZED
    if NVML_INITIALIZED:
        nvmlShutdown()
        NVML_INITIALIZED = False


def get_global_stats():
    global DEVICE_COUNT, NVML_AVAILABLE
    """Fetch global CPU, memory, and GPU usage."""
    # CPU Usage
    cpu_usage = psutil.cpu_percent(interval=0.1)
    
    # Memory Usage
    memory = psutil.virtual_memory()
    free_memory = memory.available / 1024**2  # Convert to MB

    # GPU Stats
    gpu_stats = [{"GPU Index": -1,
       "Memory Total (MB)": -1,
       "Memory Free (MB)": -1,
       "Memory Used (MB)": -1,
       "GPU Utilization (%)": -1,
       "Memory Utilization (%)": -1}
         for _ in range(DEVICE_COUNT or 1)]

    if NVML_AVAILABLE:
       try:
           DEVICE_COUNT = nvmlDeviceGetCount()  # Check for available devices
           for gpu_index in range(DEVICE_COUNT):
               handle = nvmlDeviceGetHandleByIndex(gpu_index)
               mem_info = nvmlDeviceGetMemoryInfo(handle)
               utilization = nvmlDeviceGetUtilizationRates(handle)
               gpu_stats[gpu_index] = {
                   "GPU Index": gpu_index,
                   "Memory Total (MB)": mem_info.total / 1024**2,
                   "Memory Free (MB)": mem_info.free / 1024**2,
                   "Memory Used (MB)": mem_info.used / 1024**2,
                   "GPU Utilization (%)": utilization.gpu,
                   "Memory Utilization (%)": utilization.memory,
               }
       except NVMLError_LibraryNotFound:
            stats["GPU Stats"].append({"Error": "NVML Library not found; skipping GPU monitoring."})
       except Exception as e:
           a=10
           #print(f"Error retrieving GPU stats: {e}")

    else:
        gpu_stats.append({"Error": "NVML not available; skipping GPU monitoring."})

    
    return {
        "CPU Usage (%)": cpu_usage,
        "Free Memory (MB)": free_memory,
        "GPU Stats": gpu_stats,
    }

def get_pid_stats(pid):
    global DEVICE_COUNT, NVML_AVAILABLE

    """Fetch CPU, memory, and GPU usage for a specific PID."""
    if NVML_AVAILABLE:
        try:
            process = psutil.Process(pid)
            cpu_usage = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / 1024**2  # Resident Set Size (in MB)
            
            # GPU Usage (if any)
            nvmlInit()
            gpu_usage = [{"GPU Index": -1,
               "Memory Total (MB)": -1,
               "Memory Free (MB)": -1,
               "Memory Used (MB)": -1,
               "GPU Utilization (%)": -1,
               "Memory Utilization (%)": -1}
                 for _ in range(DEVICE_COUNT or 1)]
            try:
                DEVICE_COUNT = nvmlDeviceGetCount() # Check for available devices
                for gpu_index in range(DEVICE_COUNT):
                    handle = nvmlDeviceGetHandleByIndex(gpu_index)
                    compute_procs = nvmlDeviceGetComputeRunningProcesses(handle)
                    graphics_procs = nvmlDeviceGetGraphicsRunningProcesses(handle)
                    all_procs = compute_procs + graphics_procs
                    for proc in all_procs:
                        if proc.pid == pid:
                            gpu_usage.append({
                                "GPU Index": gpu_index,
                                "Memory Used (MB)": proc.usedGpuMemory / 1024**2,
                            })
            except Exception as e:
                a=10
                #print(f"Error retrieving GPU stats for PID {pid}: {e}")
            
            return {
                "CPU Usage (%)": cpu_usage,
                "Memory Usage (MB)": memory_usage,
                "GPU Usage": gpu_usage,
            }
        except psutil.NoSuchProcess:
            return f"Process with PID {pid} not found."


def monitor_resources(pid=None, interval=5, outfile=None):
    """
    Periodically monitor and print resource usage to console or file.
    
    Args:
        pid (int, optional): Process ID to monitor specific process stats.
        interval (int): Time interval (in seconds) between measurements.
        outfile (str, optional): File path to write the output.
    """
    # Open output file if specified
    output = open(outfile, 'w') if outfile else sys.stdout

    # Print header line
    header = (
        "Processing Time (sec)\tCPU Usage (%)\tFree Memory (MB)\tGPU Index\t"
        "Memory Total (MB)\tMemory Free (MB)\tMemory Used (MB)\t"
        "GPU Utilization (%)\tMemory Utilization (%)"
    )

    if pid is not None:
        header += "\tPID CPU Usage (%)\tPID Memory Usage (MB)\tPID GPU Index\tPID Memory Used (MB)"

    print(header, file=output )

    # Start time for accurate time tracking
    start_time = time.time()

    try:
        while True:
            # Fetch global stats (dummy example below; replace with your function)
            global_stats = get_global_stats()  # Replace with real implementation
            ptime = time.time() - start_time

            # Construct the row for global stats
            row = f"{ptime:.2f}\t{global_stats['CPU Usage (%)']}\t{global_stats['Free Memory (MB)']}"
            for gpu in global_stats["GPU Stats"]:
                row += (
                    f"\t{gpu['GPU Index']}\t{gpu['Memory Total (MB)']}\t"
                    f"{gpu['Memory Free (MB)']}\t{gpu['Memory Used (MB)']}\t"
                    f"{gpu['GPU Utilization (%)']}\t{gpu['Memory Utilization (%)']}"
                )

            # Include PID stats if specified
            if pid is not None:
                pid_stats = get_pid_stats(pid)  # Replace with real implementation
                if isinstance(pid_stats, str):  # Handle errors in PID fetching
                    error_msg = f"Error fetching PID {pid} stats: {pid_stats}"
                    if output:
                        output.write(error_msg + "\n")
                    else:
                        print(error_msg)
                else:
                    pid_row = f"\t{pid_stats['CPU Usage (%)']}\t{pid_stats['Memory Usage (MB)']}"
                    for gpu in pid_stats["GPU Usage"]:
                        pid_row += f"\t{gpu['GPU Index']}\t{gpu['Memory Used (MB)']}"
                    row += pid_row

            print ( row, file=output )

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
    finally:
        if output is not sys.stdout:
            output.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor system and process resource usage.")
    parser.add_argument(
        "-p", "--pid", type=int, help="PID of the process to monitor (optional)."
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=5, help="Interval between checks in seconds."
    )
    parser.add_argument(
        "-o", "--outfile", type=str, default=None, help="output the measurements to a file instead of stdout."
    )
    args = parser.parse_args()

    try:
        initialize_nvml()
        monitor_resources(pid=args.pid, interval=args.interval, outfile=args.outfile )
        shutdown_nvml()
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

