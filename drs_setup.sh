#! /bin/bash

# documentation at: https://www.phenix.bnl.gov/~purschke/rcdaq/

# 2538 channels 1-4 working as of June 12 2025

args=(
    1        # event type
    1001     # subid
    # 2702   # serial number, only used with device_drs_by_serialnumber and not with device_drs
    0x30     # trigger channel (0x21 == ch 1 trigger, 0x28 == ch 4 trigger, 0x30 == ext trigger)
    -20      # trigger threshold [mV] (doesn't work with ext trigger, which requires >= 1.1V to trigger)
    n        # slope (n/p) (doesn't work with ext trigger, which requires p slope)
    800      # delay [ns]
    1        # speed (0 = .5GS/s, 1 = 1GS/s, 2 = 2GS/s, 3 = 5GS/s)
    0        # start channel
    # 0      # nch (discard first n samples, causes slowdown, do not use) https://www.phenix.bnl.gov/~purschke/rcdaq/rcdaq_doc.pdf page 44
    # 0      # baseline [mV] (discards last n samples, do not use)
)

export AREA=rcdaq_server_log_directory

# Create directory if it doesn't exist
[ -d "$AREA" ] || mkdir -p "$AREA"

sudo chmod -R 777 /dev/bus/usb/

if ! rcdaq_client daq_status > /dev/null 2>&1 ; then
    echo "No rcdaq_server currently running."
else
    echo -en "Ending existing rcdaq session ... "
    rcdaq_client daq_end > /dev/null 2>&1 # end run
    echo -n "waiting for 0.5s ... "
    sleep 0.5
    rcdaq_client daq_shutdown > /dev/null 2>&1 # shutdown server
    echo -n "waiting for 2s ... "
    sleep 2
    echo -e "done."
fi

echo -n "Starting new server ... "
rcdaq_server > "$AREA/rcdaq.log" 2>&1 &
echo -n "waiting for 2s ... "
sleep 2
echo -e "done.\n"

if ! rcdaq_client daq_status -l | grep -q "DRS Plugin" ; then

    echo -n "Loading the DRS4 rcdaq plugin ... "
    rcdaq_client load librcdaqplugin_drs.so
    echo "done."
else
    echo "DRS Plugin is already loaded."
fi

echo

# clear readlists
rcdaq_client daq_clear_readlist

# from rcdaq_client daq_status -ll, DRS4 plugin provides:
# List of loaded Plugins:
# - DRS Plugin, provides -
#  -     device_drs
#         (evttype, subid, triggerchannel, triggerthreshold[mV], slope[n/p], delay[ns], speed, start_ch, nch, baseline[mV]) - DRS4 Eval Board
#  -     device_drs_by_serialnumber
#         (evttype, subid, serialnumber, triggerchannel, triggerthreshold[mV], slope[n/p], delay[ns], speed, start_ch, nch, baseline[mV]) - DRS4 Eval Board

echo -e "\nCreating device_drs with args: ${args[*]}"
rcdaq_client create_device device_drs -- "${args[@]}"
echo -n "Device created: "

# prints readlists
output=$(rcdaq_client daq_list_readlist 2>&1)

if echo "$output" | grep -q "not functional"; then
    echo -e "\x1b[31m$output\x1b[0m"
else
    echo -e "\x1b[32m$output\x1b[0m"
fi

# prints status of the server
echo -en "\nServer status: "
rcdaq_client daq_status

if grep -q "Error starting server on port" "$AREA/rcdaq.log"; then
    echo -e "\x1b[31mError: Server failed to start due to port issue. Make sure to kill rcdaq server before closing terminal.\x1b[0m"
else
    echo -e "\x1b[32mServer started successfully.\x1b[0m"
fi

# (optional) start the run
# echo -en "\nStarting run "
# rcdaq_client daq_open
# rcdaq_client daq_begin