import gc
import os
import time
import ROOT
import signal
import subprocess



shared_lib_path = 'libPMT_scan.so'
assert os.path.exists(shared_lib_path), f"Shared library {shared_lib_path} not found. Please compile it first."

try:
    subprocess.run(['rcdaq_client', 'daq_status'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    print("No existing rcdaq session found, did you run drs_setup.sh?")
    exit(1)

ROOT.gROOT.ProcessLine(f'gSystem->Load("{shared_lib_path}");')
ROOT.gROOT.ProcessLine('#include <pmonitor/pmonitor.h>')
xy_poss = [(123, 456), (789, 1011), (1213, 1415), (1617, 1819), (123, 333), (456, 789), (1011, 1213), (1415, 1617)]
n_runs = 400  # Number of runs for each position

for xpos, ypos in xy_poss[:2]:
    start_time = time.time()
    print(f'\nTaking data at position ({xpos}, {ypos}) for {n_runs} runs ... ')

    subprocess.run("rcdaq_client daq_begin > /dev/null", shell=True)

    ROOT.gROOT.ProcessLine('rcdaqopen();')
    ROOT.gROOT.ProcessLine(f'prun({n_runs});')
    ROOT.gROOT.ProcessLine('pclose();')

    peak_histogram = ROOT.gDirectory.Get("peak_histogram")
    if not peak_histogram:
        print("\x1b[31mError: peak_histogram not found in the current directory!\x1b[0m")
        continue

    mean_peak = peak_histogram.GetMean()
    n_entires = peak_histogram.GetEntries()
    peak_histogram.Reset()

    elapsed_time = time.time() - start_time
    print(f'Got mean peak: {mean_peak:.2f} mV, {n_entires} entries in {elapsed_time:.2f} seconds ({n_entires / elapsed_time:.2f} entries/s).')
    subprocess.run("rcdaq_client daq_end > /dev/null", shell=True)
    gc.collect()


def kill_rcdaq_server():
    try:
        # Use pgrep to find the PID of the rcdaq_server
        result = subprocess.run(['pgrep', 'rcdaq_server'], capture_output=True, text=True, check=True)
        pids = result.stdout.strip().split()

        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)  # Use SIGKILL for immediate termination
            print(f"Terminated rcdaq_server with PID {pid}")

    except subprocess.CalledProcessError:
        print("No rcdaq_server process found.")
    except Exception as e:
        print(f"An error occurred: {e}")


print("Kill rcdaq_server so next run will work properly ...")
kill_rcdaq_server()