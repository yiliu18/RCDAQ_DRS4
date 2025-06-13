import os
import time
import ROOT
import subprocess



xy_poss = [(123, 456), (789, 1011), (1213, 1415), (1617, 1819), (123, 333), (456, 789), (1011, 1213), (1415, 1617)]
n_events = 400  # Number of runs for each position

def start_rcdaq():
    print('Starting rcdaq run ... ', end='')
    shared_lib_path = 'libPMT_scan.so'
    assert os.path.exists(shared_lib_path), f'Shared library {shared_lib_path} not found. Please compile it first.'

    try:
        subprocess.run(['rcdaq_client', 'daq_status'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print('No existing rcdaq server found, did you run drs_setup.sh?')
        exit(1)

    subprocess.run('rcdaq_client daq_begin > /dev/null', shell=True)

    ROOT.gROOT.ProcessLine(f'gSystem->Load("{shared_lib_path}");')
    ROOT.gROOT.ProcessLine('#include <pmonitor/pmonitor.h>')
    ROOT.gROOT.ProcessLine('rcdaqopen();')
    # ROOT.gROOT.ProcessLine('ptestopen();')
    ROOT.gROOT.ProcessLine('pstart();')

    peak_histogram = ROOT.gDirectory.Get('peak_histogram')
    if not peak_histogram:
        print('\x1b[31mError: peak_histogram not found in the current directory!\x1b[0m')
        exit(1)
    print('done.')
    return peak_histogram

def end_rcdaq():
    print('\nStopping run and killing rcdaq server ...')
    ROOT.gROOT.ProcessLine('pstop();')
    ROOT.gROOT.ProcessLine('pclose();')
    subprocess.run('rcdaq_client daq_end > /dev/null', shell=True)
    subprocess.run('rcdaq_client daq_shutdown > /dev/null', shell=True)

    print('Done.')

peak_histogram = start_rcdaq()

for xpos, ypos in xy_poss[:2]:
    start_time = time.time()
    print(f'\nTaking data at position ({xpos}, {ypos}) for {n_events} events ... ', end='', flush=True)

    ROOT.gROOT.ProcessLine(f'set_events_to_process({n_events});')

    # wait for the peak histogram to be filled
    while (n_events_finished := peak_histogram.GetEntries()) < n_events:
        print(f'\rTaking data at position ({xpos}, {ypos}) for {n_events} events ... {n_events_finished:.0f}/{n_events} ... ', end='', flush=True)
        time.sleep(0.1)

    print(f'\rTaking data at position ({xpos}, {ypos}) for {n_events} events ... {n_events_finished:.0f}/{n_events} ... done.')

    mean_peak = peak_histogram.GetMean()
    n_entires = peak_histogram.GetEntries()

    elapsed_time = time.time() - start_time
    print(f'Got mean peak: {mean_peak:.2f} mV, {n_entires} entries in {elapsed_time:.2f} seconds ({n_entires / elapsed_time:.2f} entries/s).')

end_rcdaq()